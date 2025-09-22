from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from asgiref.sync import sync_to_async
from django.db import IntegrityError
from .models import RazorpayPaymentGateway
from HindAi_users.models import HindAIUser
from decimal import Decimal
import httpx
import base64
import json

router = APIRouter()

# Razorpay credentials
YOUR_KEY_ID = 'rzp_test_q8KfxoL8kzFTYm'
YOUR_KEY_SECRET = 'RUlbnWNlzS5RBYGWgsKmCMEI'

class OrderRequest(BaseModel):
    amount: int  # Amount in paise (e.g., 50000 = ₹500)
    currency: str = "INR"
    receipt: str
    username: Optional[str] = None  # Will be used to find the HindAIUser
    notes: Optional[dict] = None

class OrderResponse(BaseModel):
    id: str
    entity: str
    amount: int
    currency: str
    receipt: str
    status: str
    created_at: int

class UserOrderIdsResponse(BaseModel):
    username: str
    total_orders: int
    order_ids: List[str]

@router.post("/create-order", response_model=OrderResponse)
async def create_razorpay_order(order_request: OrderRequest):
    """
    Create a Razorpay order and save to database
    """
    try:
        # Prepare the order data
        order_data = {
            "amount": order_request.amount,
            "currency": order_request.currency,
            "receipt": order_request.receipt,
            "notes": order_request.notes or {}
        }
        
        # Add username to notes if provided
        if order_request.username:
            order_data["notes"]["username"] = order_request.username
        
        # Create Basic Auth header
        credentials = f"{YOUR_KEY_ID}:{YOUR_KEY_SECRET}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()
        
        headers = {
            "Authorization": f"Basic {encoded_credentials}",
            "Content-Type": "application/json"
        }
        
        # Make request to Razorpay API
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.razorpay.com/v1/orders",
                json=order_data,
                headers=headers
            )
            
            if response.status_code == 200:
                order_response = response.json()
                
                # Save to database
                await save_order_to_db(order_response, order_request.username, order_request.notes)
                
                return OrderResponse(**order_response)
            else:
                error_data = response.json() if response.content else {"error": "Unknown error"}
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Razorpay API error: {error_data}"
                )
                
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Network error while connecting to Razorpay: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error creating order: {str(e)}"
        )

@sync_to_async
def save_order_to_db(razorpay_response: dict, username: str = None, notes: dict = None):
    """
    Save Razorpay order to database with user foreign key
    """
    try:
        user = None
        if username:
            try:
                user = HindAIUser.objects.get(username=username)
            except HindAIUser.DoesNotExist:
                # User not found, you can either create or leave as None
                pass
        
        order = RazorpayPaymentGateway.objects.create(
            razorpay_order_id=razorpay_response['id'],
            entity=razorpay_response['entity'],
            amount=razorpay_response['amount'],
            currency=razorpay_response['currency'],
            receipt=razorpay_response['receipt'],
            status=razorpay_response['status'],
            created_at=razorpay_response['created_at'],
            user=user,
            notes=notes or {}
        )
        return order
    except IntegrityError:
        # Order already exists
        raise HTTPException(
            status_code=400,
            detail="Order with this ID already exists"
        )

@router.get("/orders")
async def get_all_orders():
    """
    Get all saved orders with user details
    """
    orders = await sync_to_async(list)(
        RazorpayPaymentGateway.objects.select_related('user').all().values(
            'razorpay_order_id', 'amount', 'currency', 'receipt', 
            'status', 'user__username', 'user__email', 'created_timestamp'
        )
    )
    return orders

@router.get("/orders/user/{username}")
async def get_orders_by_username(username: str):
    """
    Get all orders for a specific user
    """
    try:
        orders = await sync_to_async(list)(
            RazorpayPaymentGateway.objects.filter(user__username=username).values(
                'razorpay_order_id', 'amount', 'currency', 'receipt', 
                'status', 'created_timestamp'
            )
        )
        if not orders:
            raise HTTPException(
                status_code=404,
                detail=f"No orders found for user: {username}"
            )
        return orders
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching orders: {str(e)}"
        )

@router.get("/user/{username}/order-ids", response_model=UserOrderIdsResponse)
async def get_user_order_ids(username: str):
    """
    Get all created order IDs for a specific user by username
    """
    try:
        # Check if user exists
        user_exists = await sync_to_async(HindAIUser.objects.filter(username=username).exists)()
        if not user_exists:
            raise HTTPException(
                status_code=404,
                detail=f"User '{username}' not found"
            )
        
        # Get all order IDs for the user
        order_ids = await sync_to_async(list)(
            RazorpayPaymentGateway.objects.filter(user__username=username)
            .values_list('razorpay_order_id', flat=True)
            .order_by('-created_timestamp')
        )
        
        return UserOrderIdsResponse(
            username=username,
            total_orders=len(order_ids),
            order_ids=order_ids
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching order IDs: {str(e)}"
        )

