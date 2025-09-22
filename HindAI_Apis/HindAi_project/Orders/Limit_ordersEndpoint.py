from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import sys
import os
from asgiref.sync import sync_to_async
import json

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from common_import import *
from .orders_codes.BUY_Limit_Order import Buy_Limit_Order
from .orders_codes.SELL_Limit_Order import SELL_Limit_Order
from .orders_codes.Order_Status import get_order_status
from .orders_codes.cancel_order import cancel_order
from .models import LimitOrder
from HindAi_users.models import HindAIUser as User

from accounts.models import SnaptradeUsers 

router = APIRouter()

class LimitOrderRequest(BaseModel):
    username: str
    account_id: str
    symbol: str
    unit: int
    limit_price: float
    stop_price: Optional[float] = None
    time_in_force: Optional[str] = "Day"  # Default to Day order

class LimitOrderResponse(BaseModel):
    success: bool
    message: str
    order_id: Optional[str] = None
    data: Optional[dict] = None
    error_code: Optional[str] = None
    existing_order_id: Optional[str] = None

class LimitOrderStatusRequest(BaseModel):
    username: str
    account_id: str

class LimitOrderStatusResponse(BaseModel):
    success: bool
    message: str
    orders: List[dict] = []
    updated_orders: int = 0

class CancelLimitOrderRequest(BaseModel):
    username: str
    account_id: str
    brokerage_order_id: str

class CancelLimitOrderResponse(BaseModel):
    success: bool
    message: str
    order_id: Optional[str] = None
    data: Optional[dict] = None
    error_code: Optional[str] = None

def parse_snaptrack_error(error_str: str) -> dict:
    """Parse SnapTrade error and extract meaningful information"""
    try:
        # Extract JSON from the error string
        if "'detail':" in error_str:
            start = error_str.find("{'detail':")
            end = error_str.rfind("}")
            if start != -1 and end != -1:
                error_json_str = error_str[start:end+1].replace("'", '"')
                error_data = json.loads(error_json_str)
                
                return {
                    "error_message": error_data.get('detail', 'Unknown error'),
                    "error_code": error_data.get('code', ''),
                    "status_code": error_data.get('status_code', 400),
                    "existing_order_id": error_data.get('raw_error', {}).get('body', {}).get('existing_order_id'),
                    "reject_reason": error_data.get('raw_error', {}).get('body', {}).get('reject_reason'),
                    "raw_message": error_data.get('raw_error', {}).get('body', {}).get('message')
                }
    except:
        pass
    
    # Fallback parsing
    if "potential wash trade detected" in error_str:
        return {
            "error_message": "Potential wash trade detected. Cannot place opposite order while existing order exists.",
            "error_code": "1119",
            "status_code": 400,
            "reject_reason": "wash trade prevention"
        }
    
    return {
        "error_message": "Unknown trading error occurred",
        "error_code": "UNKNOWN",
        "status_code": 400
    }


async def process_limit_order(order_request: LimitOrderRequest, order_function, action_type: str):
    """Common function to process both BUY and SELL limit orders"""
    try:
        # Get Django user by username
        try:
            django_user = await sync_to_async(User.objects.get)(username=order_request.username)
        except User.DoesNotExist:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Get SnapTrade user details
        try:
            snaptrade_user = await sync_to_async(SnaptradeUsers.objects.get)(user=django_user)
        except SnaptradeUsers.DoesNotExist:
            raise HTTPException(status_code=404, detail="SnapTrade user not found for this user")
        
        # Execute the Limit Order using actual function
        try:
            response = await sync_to_async(order_function)(
                user_id=snaptrade_user.userId,
                user_secret=snaptrade_user.userSecret,
                account_id=order_request.account_id,
                symbol=order_request.symbol,
                price=order_request.limit_price,
                stop=order_request.stop_price,
                units=order_request.unit,
                time_in_force=order_request.time_in_force
            )
            
        except Exception as trading_error:
            error_info = parse_snaptrack_error(str(trading_error))
            
            return LimitOrderResponse(
                success=False,
                message=error_info["error_message"],
                error_code=error_info["error_code"],
                existing_order_id=error_info.get("existing_order_id"),
                data={
                    "reject_reason": error_info.get("reject_reason"),
                    "raw_message": error_info.get("raw_message"),
                    "suggestions": [
                        "Check for existing opposite orders",
                        "Cancel conflicting orders first",
                        "Verify limit price is reasonable"
                    ] if "wash trade" in error_info["error_message"] else []
                }
            )
        
        # Parse response and save to database
        if response:
            order_data = response
            
            # Create LimitOrder instance
            limit_order_obj = await sync_to_async(LimitOrder.objects.create)(
                user=django_user,
                action=order_data.get('action'),
                brokerage_order_id=order_data.get('brokerage_order_id'),
                status=order_data.get('status'),
                total_quantity=order_data.get('total_quantity'),
                filled_quantity=order_data.get('filled_quantity'),
                canceled_quantity=order_data.get('canceled_quantity'),
                open_quantity=order_data.get('open_quantity'),
                execution_price=order_data.get('execution_price'),
                limit_price=order_data.get('limit_price'),
                stop_price=order_data.get('stop_price'),
                order_type=order_data.get('order_type'),
                time_in_force=order_data.get('time_in_force'),
                symbol=order_data.get('symbol'),
                option_symbol=order_data.get('option_symbol'),
                time_placed=datetime.fromisoformat(order_data.get('time_placed').replace('Z', '+00:00')) if order_data.get('time_placed') else None,
                time_executed=datetime.fromisoformat(order_data.get('time_executed').replace('Z', '+00:00')) if order_data.get('time_executed') else None,
                time_updated=datetime.fromisoformat(order_data.get('time_updated').replace('Z', '+00:00')) if order_data.get('time_updated') else None,
                quote_currency=order_data.get('quote_currency'),
                quote_universal_symbol=order_data.get('quote_universal_symbol'),
                child_brokerage_order_ids=order_data.get('child_brokerage_order_ids'),
            )
            
            # Extract universal symbol data
            universal_symbol = order_data.get('universal_symbol', {})
            if universal_symbol:
                limit_order_obj.universal_symbol_id = universal_symbol.get('id')
                limit_order_obj.raw_symbol = universal_symbol.get('raw_symbol')
                limit_order_obj.symbol_name = universal_symbol.get('symbol')
                limit_order_obj.description = universal_symbol.get('description')
                limit_order_obj.figi_code = universal_symbol.get('figi_code')
                limit_order_obj.logo_url = universal_symbol.get('logo_url')
                
                # Extract FIGI instrument data
                figi_instrument = universal_symbol.get('figi_instrument', {})
                if figi_instrument:
                    limit_order_obj.figi_share_class = figi_instrument.get('figi_share_class')
                
                # Extract exchange data
                exchange = universal_symbol.get('exchange', {})
                if exchange:
                    limit_order_obj.exchange_id = exchange.get('id')
                    limit_order_obj.exchange_code = exchange.get('code')
                    limit_order_obj.exchange_name = exchange.get('name')
                    limit_order_obj.exchange_mic_code = exchange.get('mic_code')
                    limit_order_obj.exchange_timezone = exchange.get('timezone')
                    limit_order_obj.exchange_suffix = exchange.get('suffix')
                    limit_order_obj.exchange_start_time = exchange.get('start_time')
                    limit_order_obj.exchange_close_time = exchange.get('close_time')
                
                # Extract currency data
                currency = universal_symbol.get('currency', {})
                if currency:
                    limit_order_obj.currency_id = currency.get('id')
                    limit_order_obj.currency_code = currency.get('code')
                    limit_order_obj.currency_name = currency.get('name')
                
                # Extract security type data
                security_type = universal_symbol.get('type', {})
                if security_type:
                    limit_order_obj.security_type_id = security_type.get('id')
                    limit_order_obj.security_type_code = security_type.get('code')
                    limit_order_obj.security_type_description = security_type.get('description')
                    limit_order_obj.security_type_is_supported = security_type.get('is_supported', True)
            
            # Save the updated object
            await sync_to_async(limit_order_obj.save)()
            
            return LimitOrderResponse(
                success=True,
                message=f"Limit {action_type} order placed successfully",
                order_id=order_data.get('brokerage_order_id'),
                data=order_data
            )
        else:
            return LimitOrderResponse(
                success=False,
                message="Failed to place limit order - no response received",
                error_code="NO_RESPONSE"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in {action_type} limit order: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error placing {action_type} limit order: {str(e)}")

@router.post("/limit-order-BUY", response_model=LimitOrderResponse)
async def create_buy_limit_order(order_request: LimitOrderRequest):
    return await process_limit_order(order_request, Buy_Limit_Order, "BUY")

@router.post("/limit-order-SELL", response_model=LimitOrderResponse)
async def create_sell_limit_order(order_request: LimitOrderRequest):
    return await process_limit_order(order_request, SELL_Limit_Order, "SELL")

@router.post("/cancel-limit-order", response_model=CancelLimitOrderResponse)
async def cancel_limit_order_endpoint(cancel_request: CancelLimitOrderRequest):
    try:
        # Get Django user by username
        try:
            django_user = await sync_to_async(User.objects.get)(username=cancel_request.username)
        except User.DoesNotExist:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Get SnapTrade user details
        try:
            snaptrade_user = await sync_to_async(SnaptradeUsers.objects.get)(user=django_user)
        except SnaptradeUsers.DoesNotExist:
            raise HTTPException(status_code=404, detail="SnapTrade user not found for this user")
        
        # Check if order exists in database
        try:
            existing_order = await sync_to_async(LimitOrder.objects.get)(
                brokerage_order_id=cancel_request.brokerage_order_id,
                user=django_user
            )
        except LimitOrder.DoesNotExist:
            raise HTTPException(status_code=404, detail="Limit order not found in database")
        
        # Check if order is already canceled or executed
        if existing_order.status in ['CANCELLED', 'CANCELED', 'EXECUTED', 'FILLED']:
            return CancelLimitOrderResponse(
                success=False,
                message=f"Cannot cancel order. Order is already {existing_order.status}",
                order_id=cancel_request.brokerage_order_id,
                error_code="ORDER_NOT_CANCELLABLE"
            )
        
        # Cancel order via SnapTrade API
        try:
            cancel_response = await sync_to_async(cancel_order)(
                account_id=cancel_request.account_id,
                user_id=snaptrade_user.userId,
                user_secret=snaptrade_user.userSecret,
                brokerage_order_id=cancel_request.brokerage_order_id
            )
            
        except Exception as cancel_error:
            error_info = parse_snaptrack_error(str(cancel_error))
            
            return CancelLimitOrderResponse(
                success=False,
                message=f"Failed to cancel order: {error_info['error_message']}",
                order_id=cancel_request.brokerage_order_id,
                error_code=error_info["error_code"],
                data={
                    "reject_reason": error_info.get("reject_reason"),
                    "raw_message": error_info.get("raw_message")
                }
            )
        
        # Update order status in database
        if cancel_response:
            existing_order.status = cancel_response.get('status', 'CANCELLED')
            existing_order.canceled_quantity = cancel_response.get('canceled_quantity', existing_order.total_quantity)
            existing_order.open_quantity = cancel_response.get('open_quantity', 0)
            
            if cancel_response.get('time_updated'):
                existing_order.time_updated = datetime.fromisoformat(
                    cancel_response.get('time_updated').replace('Z', '+00:00')
                )
            else:
                existing_order.time_updated = datetime.now()
            
            await sync_to_async(existing_order.save)()
            
            return CancelLimitOrderResponse(
                success=True,
                message="Limit order cancelled successfully",
                order_id=cancel_request.brokerage_order_id,
                data={
                    "status": existing_order.status,
                    "canceled_quantity": str(existing_order.canceled_quantity) if existing_order.canceled_quantity else None,
                    "time_updated": existing_order.time_updated.isoformat() if existing_order.time_updated else None,
                    "original_response": cancel_response
                }
            )
        else:
            return CancelLimitOrderResponse(
                success=False,
                message="Failed to cancel order - no response from API",
                order_id=cancel_request.brokerage_order_id,
                error_code="NO_RESPONSE"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in cancel_limit_order: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error cancelling limit order: {str(e)}")

@router.post("/limit-order-status", response_model=LimitOrderStatusResponse)
async def get_and_update_limit_order_status(status_request: LimitOrderStatusRequest):
    try:
        # Get Django user by username
        try:
            django_user = await sync_to_async(User.objects.get)(username=status_request.username)
        except User.DoesNotExist:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Get SnapTrade user details
        try:
            snaptrade_user = await sync_to_async(SnaptradeUsers.objects.get)(user=django_user)
        except SnaptradeUsers.DoesNotExist:
            raise HTTPException(status_code=404, detail="SnapTrade user not found for this user")
        
        # Fetch order status from SnapTrade API
        api_orders = await sync_to_async(get_order_status)(
            user_id=snaptrade_user.userId,
            account_id=status_request.account_id,
            user_secret=snaptrade_user.userSecret
        )
        
        if not api_orders:
            return LimitOrderStatusResponse(
                success=True,
                message="No limit orders found",
                orders=[],
                updated_orders=0
            )
        
        updated_count = 0
        orders_data = []
        
        # Filter for limit orders and process each one
        for api_order in api_orders:
            # Check if this is a limit order (has limit_price)
            if api_order.get('limit_price') is None:
                continue
                
            brokerage_order_id = api_order.get('brokerage_order_id')
            
            if brokerage_order_id:
                try:
                    # Find existing order in database
                    existing_order = await sync_to_async(
                        LimitOrder.objects.get
                    )(brokerage_order_id=brokerage_order_id, user=django_user)
                    
                    # Update existing order with latest data
                    existing_order.status = api_order.get('status', existing_order.status)
                    existing_order.filled_quantity = api_order.get('filled_quantity', existing_order.filled_quantity)
                    existing_order.canceled_quantity = api_order.get('canceled_quantity', existing_order.canceled_quantity)
                    existing_order.open_quantity = api_order.get('open_quantity', existing_order.open_quantity)
                    existing_order.execution_price = api_order.get('execution_price', existing_order.execution_price)
                    existing_order.limit_price = api_order.get('limit_price', existing_order.limit_price)
                    
                    # Update timestamps if provided
                    if api_order.get('time_executed'):
                        existing_order.time_executed = datetime.fromisoformat(
                            api_order.get('time_executed').replace('Z', '+00:00')
                        )
                    if api_order.get('time_updated'):
                        existing_order.time_updated = datetime.fromisoformat(
                            api_order.get('time_updated').replace('Z', '+00:00')
                        )
                    
                    await sync_to_async(existing_order.save)()
                    updated_count += 1
                    
                except LimitOrder.DoesNotExist:
                    # Order not in database, create new one
                    universal_symbol = api_order.get('universal_symbol', {})
                    exchange = universal_symbol.get('exchange', {})
                    currency = universal_symbol.get('currency', {})
                    security_type = universal_symbol.get('type', {})
                    figi_instrument = universal_symbol.get('figi_instrument', {})
                    
                    new_order = await sync_to_async(LimitOrder.objects.create)(
                        user=django_user,
                        action=api_order.get('action'),
                        brokerage_order_id=brokerage_order_id,
                        status=api_order.get('status'),
                        total_quantity=api_order.get('total_quantity'),
                        filled_quantity=api_order.get('filled_quantity'),
                        canceled_quantity=api_order.get('canceled_quantity'),
                        open_quantity=api_order.get('open_quantity'),
                        execution_price=api_order.get('execution_price'),
                        limit_price=api_order.get('limit_price'),
                        stop_price=api_order.get('stop_price'),
                        order_type=api_order.get('order_type'),
                        time_in_force=api_order.get('time_in_force'),
                        symbol=api_order.get('symbol'),
                        option_symbol=api_order.get('option_symbol'),
                        time_placed=datetime.fromisoformat(api_order.get('time_placed').replace('Z', '+00:00')) if api_order.get('time_placed') else None,
                        time_executed=datetime.fromisoformat(api_order.get('time_executed').replace('Z', '+00:00')) if api_order.get('time_executed') else None,
                        time_updated=datetime.fromisoformat(api_order.get('time_updated').replace('Z', '+00:00')) if api_order.get('time_updated') else None,
                        quote_currency=api_order.get('quote_currency'),
                        quote_universal_symbol=api_order.get('quote_universal_symbol'),
                        child_brokerage_order_ids=api_order.get('child_brokerage_order_ids'),
                        # Universal symbol data
                        universal_symbol_id=universal_symbol.get('id'),
                        raw_symbol=universal_symbol.get('raw_symbol'),
                        symbol_name=universal_symbol.get('symbol'),
                        description=universal_symbol.get('description'),
                        figi_code=universal_symbol.get('figi_code'),
                        figi_share_class=figi_instrument.get('figi_share_class'),
                        logo_url=universal_symbol.get('logo_url'),
                        # Exchange data
                        exchange_id=exchange.get('id'),
                        exchange_code=exchange.get('code'),
                        exchange_name=exchange.get('name'),
                        exchange_mic_code=exchange.get('mic_code'),
                        exchange_timezone=exchange.get('timezone'),
                        exchange_suffix=exchange.get('suffix'),
                        exchange_start_time=exchange.get('start_time'),
                        exchange_close_time=exchange.get('close_time'),
                        # Currency data
                        currency_id=currency.get('id'),
                        currency_code=currency.get('code'),
                        currency_name=currency.get('name'),
                        # Security type data
                        security_type_id=security_type.get('id'),
                        security_type_code=security_type.get('code'),
                        security_type_description=security_type.get('description'),
                        security_type_is_supported=security_type.get('is_supported', True),
                    )
                    updated_count += 1
            
            # Format order data for response
            orders_data.append({
                'brokerage_order_id': api_order.get('brokerage_order_id'),
                'action': api_order.get('action'),
                'symbol': api_order.get('universal_symbol', {}).get('raw_symbol', api_order.get('symbol')),
                'status': api_order.get('status'),
                'total_quantity': str(api_order.get('total_quantity', 0)),
                'filled_quantity': str(api_order.get('filled_quantity', 0)),
                'limit_price': str(api_order.get('limit_price', 0)),
                'execution_price': str(api_order.get('execution_price', 0)) if api_order.get('execution_price') else None,
                'time_in_force': api_order.get('time_in_force'),
                'time_placed': api_order.get('time_placed'),
                'time_executed': api_order.get('time_executed'),
                'time_updated': api_order.get('time_updated'),
            })
        
        return LimitOrderStatusResponse(
            success=True,
            message=f"Successfully fetched and updated {updated_count} limit orders",
            orders=orders_data,
            updated_orders=updated_count
        )
        
    except Exception as e:
        print(f"Error in get_and_update_limit_order_status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching limit order status: {str(e)}")

@router.get("/limit-orders/{username}")
async def get_user_limit_orders(username: str):
    try:
        # Get Django user by username
        try:
            django_user = await sync_to_async(User.objects.get)(username=username)
        except User.DoesNotExist:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Get limit orders
        orders = await sync_to_async(list)(
            LimitOrder.objects.filter(user=django_user).order_by('-time_placed')
        )
        orders_data = []
        
        for order in orders:
            orders_data.append({
                'id': order.id,
                'brokerage_order_id': order.brokerage_order_id,
                'action': order.action,
                'symbol': order.raw_symbol,
                'total_quantity': str(order.total_quantity),
                'filled_quantity': str(order.filled_quantity) if order.filled_quantity else "0",
                'canceled_quantity': str(order.canceled_quantity) if order.canceled_quantity else "0",
                'limit_price': str(order.limit_price) if order.limit_price else None,
                'stop_price': str(order.stop_price) if order.stop_price else None,
                'status': order.status,
                'time_in_force': order.time_in_force,
                'time_placed': order.time_placed.isoformat() if order.time_placed else None,
                'time_executed': order.time_executed.isoformat() if order.time_executed else None,
                'time_updated': order.time_updated.isoformat() if order.time_updated else None,
                'execution_price': str(order.execution_price) if order.execution_price else None,
                'exchange_code': order.exchange_code,
                'currency_code': order.currency_code,
            })
        
        return {
            'success': True,
            'orders': orders_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching limit orders: {str(e)}")