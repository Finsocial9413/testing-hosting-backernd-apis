from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
from django.contrib.auth import get_user_model
from asgiref.sync import sync_to_async
from decimal import Decimal
from .models import UserCredit
from HindAi_users.models import HindAIUser


router = APIRouter()

# Request models
class AddCreditsRequest(BaseModel):
    username: str
    amount: float
    
class DeductCreditsRequest(BaseModel):
    username: str
    amount: float

# Response models
class CreditResponse(BaseModel):
    username: str
    current_credits: float
    total_credits_purchased: float
    total_credits_used: float
    message: str

class CreditBalanceResponse(BaseModel):
    username: str
    current_credits: float

@router.post("/add", response_model=CreditResponse)
async def add_credits(request: AddCreditsRequest):
    """
    Add credits to a user's account by username
    """
    try:
        if request.amount <= 0:
            raise HTTPException(status_code=400, detail="Amount must be greater than 0")
        
        # Find user by username
        @sync_to_async
        def get_user_and_credits():
            try:
                user = HindAIUser.objects.get(username=request.username)
                credit_account, created = UserCredit.objects.get_or_create(
                    user=user,
                    defaults={
                        'username': user.username,
                        'current_credits': Decimal('0.00'),
                        'total_credits_purchased': Decimal('0.00'),
                        'total_credits_used': Decimal('0.00')
                    }
                )
                return user, credit_account
            except HindAIUser.DoesNotExist:
                return None, None
        
        user, credit_account = await get_user_and_credits()
        if not user:
            raise HTTPException(status_code=404, detail=f"User {request.username} not found")
        
        # Add credits
        @sync_to_async
        def add_credits_to_account():
            credit_account.add_credits(Decimal(str(request.amount)))
            credit_account.refresh_from_db()
            return credit_account
        
        updated_account = await add_credits_to_account()
        
        return {
            "username": updated_account.username,
            "current_credits": float(updated_account.current_credits),
            "total_credits_purchased": float(updated_account.total_credits_purchased),
            "total_credits_used": float(updated_account.total_credits_used),
            "message": f"Successfully added {request.amount} credits"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error adding credits: {str(e)}")

@router.post("/deduct", response_model=CreditResponse)
async def deduct_credits(request: DeductCreditsRequest):
    """
    Deduct credits from a user's account by username
    """
    try:
        if request.amount <= 0:
            raise HTTPException(status_code=400, detail="Amount must be greater than 0")
        
        # Find user and credit account
        @sync_to_async
        def get_user_and_credits():
            try:
                user = HindAIUser.objects.get(username=request.username)
                credit_account = UserCredit.objects.get(user=user)
                return user, credit_account
            except HindAIUser.DoesNotExist:
                return None, None
            except UserCredit.DoesNotExist:
                return user, None
        
        user, credit_account = await get_user_and_credits()
        if not user:
            raise HTTPException(status_code=404, detail=f"User {request.username} not found")
        if not credit_account:
            raise HTTPException(status_code=404, detail=f"Credit account not found for user {request.username}")
        
        # Check if user has sufficient credits
        if credit_account.current_credits < Decimal(str(request.amount)):
            raise HTTPException(
                status_code=400, 
                detail=f"Insufficient credits. Available: {credit_account.current_credits}, Required: {request.amount}"
            )
        
        # Deduct credits
        @sync_to_async
        def deduct_credits_from_account():
            success = credit_account.deduct_credits(Decimal(str(request.amount)))
            credit_account.refresh_from_db()
            return success, credit_account
        
        success, updated_account = await deduct_credits_from_account()
        
        if not success:
            raise HTTPException(status_code=400, detail="Failed to deduct credits")
        
        return {
            "username": updated_account.username,
            "current_credits": float(updated_account.current_credits),
            "total_credits_purchased": float(updated_account.total_credits_purchased),
            "total_credits_used": float(updated_account.total_credits_used),
            "message": f"Successfully deducted {request.amount} credits"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deducting credits: {str(e)}")

@router.get("/balance/{username}", response_model=CreditBalanceResponse)
async def get_credit_balance(username: str):
    """
    Get current credit balance for a user by username.
    If user exists but credit account does not, create it and add $5 registration bonus.
    """
    try:
        @sync_to_async
        def get_or_create_with_bonus():
            try:
                user = HindAIUser.objects.get(username=username)
            except HindAIUser.DoesNotExist:
                return None, None, False
            try:
                credit_account = UserCredit.objects.get(user=user)
                created = False
            except UserCredit.DoesNotExist:
                # Create with zeroes then use model's add_credits to keep totals consistent
                credit_account = UserCredit.objects.create(
                    user=user,
                    username=user.username,
                    current_credits=Decimal('0.00'),
                    total_credits_purchased=Decimal('0.00'),
                    total_credits_used=Decimal('0.00')
                )
                # Registration bonus
                credit_account.add_credits(Decimal('5.00'))
                credit_account.refresh_from_db()
                created = True
            return user, credit_account, created

        user, credit_account, created = await get_or_create_with_bonus()

        if not user:
            raise HTTPException(status_code=404, detail=f"User {username} not found")

        return {
            "username": credit_account.username,
            "current_credits": float(credit_account.current_credits)
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting credit balance: {str(e)}")
