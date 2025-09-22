from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Union, Optional
from django.contrib.auth import get_user_model
from asgiref.sync import sync_to_async
from .models import SubscriptionPlan, UserSubscription
from HindAi_users.models import HindAIUser
from django.db import IntegrityError, transaction
from decimal import Decimal
from datetime import datetime, timedelta
from django.utils import timezone

router = APIRouter()

# Request models
class AddUserSubscriptionRequest(BaseModel):
    username: str
    subscription_plan_id: int
    payment_reference: Optional[str] = None
    auto_renewal: Optional[bool] = False

class ActivateSubscriptionRequest(BaseModel):
    username: str
    subscription_id: int

class UpdateSubscriptionStatusRequest(BaseModel):
    username: str
    subscription_id: int
    status: str  # Should be one of: 'active', 'expired', 'cancelled', 'pending'

class UpdateSubscriptionRequest(BaseModel):
    username: str
    subscription_id: int
    status: Optional[str] = None
    end_date: Optional[datetime] = None
    credits_awarded: Optional[int] = None
    is_auto_renewal: Optional[bool] = None
    payment_reference: Optional[str] = None

# Response models
class UserSubscriptionResponse(BaseModel):
    id: int
    user_email: str
    user_username: str
    plan_name: str
    plan_duration: str
    plan_price: float
    plan_credits: int
    status: str
    status_display: str
    start_date: datetime
    end_date: Optional[datetime]
    credits_awarded: int
    is_auto_renewal: bool
    payment_reference: Optional[str]
    days_remaining: int
    is_active_now: bool
    created_at: datetime
    updated_at: datetime

class AddSubscriptionResponse(BaseModel):
    success: bool
    message: str
    subscription: UserSubscriptionResponse

class UpdateSubscriptionStatusResponse(BaseModel):
    success: bool
    message: str
    subscription: UserSubscriptionResponse

@router.post("/add_subscription", response_model=AddSubscriptionResponse)
async def add_user_subscription(request: AddUserSubscriptionRequest):
    """Add a subscription to a user"""
    try:
        # Check if user exists
        try:
            user = await sync_to_async(HindAIUser.objects.get)(username=request.username)
        except HindAIUser.DoesNotExist:
            raise HTTPException(status_code=404, detail=f"User with username '{request.username}' not found")
        
        # Check if subscription plan exists
        try:
            plan = await sync_to_async(SubscriptionPlan.objects.get)(id=request.subscription_plan_id)
        except SubscriptionPlan.DoesNotExist:
            raise HTTPException(status_code=404, detail=f"Subscription plan with ID {request.subscription_plan_id} not found")
        
        # Create new subscription with proper end_date
        end_date = timezone.now() + timedelta(days=plan.days if plan.days else plan.get_duration_in_days())
        
        subscription = UserSubscription(
            user=user,
            plan=plan,
            status='pending',
            payment_reference=request.payment_reference,
            is_auto_renewal=request.auto_renewal,
            credits_awarded=0,
            end_date=end_date
        )
        
        # Save subscription
        await sync_to_async(subscription.save)()
        
        # Prepare response
        subscription_response = UserSubscriptionResponse(
            id=subscription.id,
            user_email=user.email,
            user_username=user.username,
            plan_name=plan.name,
            plan_duration=plan.get_duration_display(),
            plan_price=float(plan.price),
            plan_credits=plan.credits,
            status=subscription.status,
            status_display=subscription.get_status_display(),
            start_date=subscription.start_date,
            end_date=subscription.end_date,
            credits_awarded=subscription.credits_awarded,
            is_auto_renewal=subscription.is_auto_renewal,
            payment_reference=subscription.payment_reference,
            days_remaining=subscription.days_remaining(),
            is_active_now=subscription.is_active(),
            created_at=subscription.created_at,
            updated_at=subscription.updated_at
        )
        
        return AddSubscriptionResponse(
            success=True,
            message=f"Subscription '{plan.name}' added successfully for user '{user.username}'. Status: Pending",
            subscription=subscription_response
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error adding subscription: {str(e)}")

@router.put("/update_subscription_status", response_model=UpdateSubscriptionStatusResponse)
async def update_subscription_status(request: UpdateSubscriptionStatusRequest):
    """Update the status of a user's subscription - FULL EDIT ACCESS"""
    try:
        # Validate status
        valid_statuses = ['active', 'expired', 'cancelled', 'pending']
        if request.status not in valid_statuses:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
            )
        
        # Check if user exists
        try:
            user = await sync_to_async(HindAIUser.objects.get)(username=request.username)
        except HindAIUser.DoesNotExist:
            raise HTTPException(status_code=404, detail=f"User with username '{request.username}' not found")
        
        # Get the subscription
        try:
            subscription = await sync_to_async(UserSubscription.objects.get)(
                id=request.subscription_id,
                user=user
            )
        except UserSubscription.DoesNotExist:
            raise HTTPException(
                status_code=404, 
                detail=f"Subscription with ID {request.subscription_id} not found for user '{request.username}'"
            )
        
        # Store old status for message
        old_status = subscription.status
        
        # Use database transaction to ensure atomicity
        @sync_to_async
        def update_subscription():
            with transaction.atomic():
                # Direct field updates without readonly restrictions
                subscription.status = request.status
                
                # If activating, set proper dates and credits
                if request.status == 'active':
                    if not subscription.end_date:
                        subscription.end_date = timezone.now() + timedelta(
                            days=subscription.plan.days if subscription.plan.days else subscription.plan.get_duration_in_days()
                        )
                    
                    if subscription.credits_awarded == 0:
                        subscription.credits_awarded = subscription.plan.credits
                
                subscription.save()
                
                # Award credits within the same transaction if activating
                if request.status == 'active' and subscription.credits_awarded > 0:
                    try:
                        from user_credits.models import UserCredit
                        
                        user_credit, created = UserCredit.objects.get_or_create(
                            user=subscription.user,
                            defaults={'username': subscription.user.username}
                        )
                        
                        # Update credits
                        user_credit.current_credits += subscription.plan.credits
                        user_credit.total_credits_purchased += subscription.plan.credits
                        user_credit.save()
                    except ImportError:
                        pass  # UserCredit model not available
                    except Exception:
                        pass  # Skip credit awarding if any error occurs
                
                # Refresh from database to get updated values
                subscription.refresh_from_db()
                
                # Return all data needed for response to avoid async context issues
                return {
                    'id': subscription.id,
                    'user_email': subscription.user.email,
                    'user_username': subscription.user.username,
                    'plan_name': subscription.plan.name,
                    'plan_duration': subscription.plan.get_duration_display(),
                    'plan_price': float(subscription.plan.price),
                    'plan_credits': subscription.plan.credits,
                    'status': subscription.status,
                    'status_display': subscription.get_status_display(),
                    'start_date': subscription.start_date,
                    'end_date': subscription.end_date,
                    'credits_awarded': subscription.credits_awarded,
                    'is_auto_renewal': subscription.is_auto_renewal,
                    'payment_reference': subscription.payment_reference,
                    'days_remaining': subscription.days_remaining(),
                    'is_active_now': subscription.is_active(),
                    'created_at': subscription.created_at,
                    'updated_at': subscription.updated_at
                }
        
        # Execute the update (now returns all data)
        subscription_data = await update_subscription()
        
        # Prepare response using the data from sync context
        subscription_response = UserSubscriptionResponse(**subscription_data)
        
        return UpdateSubscriptionStatusResponse(
            success=True,
            message=f"Subscription status updated from '{old_status}' to '{request.status}' for user '{user.username}'",
            subscription=subscription_response
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating subscription status: {str(e)}")

@router.put("/update_subscription_full", response_model=UpdateSubscriptionStatusResponse)
async def update_subscription_full(request: UpdateSubscriptionRequest):
    """Update ANY field of a user's subscription - COMPLETE EDIT ACCESS"""
    try:
        # Check if user exists
        try:
            user = await sync_to_async(HindAIUser.objects.get)(username=request.username)
        except HindAIUser.DoesNotExist:
            raise HTTPException(status_code=404, detail=f"User with username '{request.username}' not found")
        
        # Get the subscription
        try:
            subscription = await sync_to_async(UserSubscription.objects.get)(
                id=request.subscription_id,
                user=user
            )
        except UserSubscription.DoesNotExist:
            raise HTTPException(
                status_code=404, 
                detail=f"Subscription with ID {request.subscription_id} not found for user '{request.username}'"
            )
        
        # Prepare update fields
        update_fields = ['updated_at']
        changes = []
        
        @sync_to_async
        def perform_full_update():
            with transaction.atomic():
                # Update all provided fields
                if request.status is not None:
                    old_status = subscription.status
                    subscription.status = request.status
                    changes.append(f"status: {old_status} → {request.status}")
                
                if request.end_date is not None:
                    old_end_date = subscription.end_date
                    subscription.end_date = request.end_date
                    changes.append(f"end_date: {old_end_date} → {request.end_date}")
                
                if request.credits_awarded is not None:
                    old_credits = subscription.credits_awarded
                    subscription.credits_awarded = request.credits_awarded
                    changes.append(f"credits_awarded: {old_credits} → {request.credits_awarded}")
                
                if request.is_auto_renewal is not None:
                    old_auto_renewal = subscription.is_auto_renewal
                    subscription.is_auto_renewal = request.is_auto_renewal
                    changes.append(f"auto_renewal: {old_auto_renewal} → {request.is_auto_renewal}")
                
                if request.payment_reference is not None:
                    old_payment_ref = subscription.payment_reference
                    subscription.payment_reference = request.payment_reference
                    changes.append(f"payment_reference: {old_payment_ref} → {request.payment_reference}")
                
                subscription.save()
                subscription.refresh_from_db()
                
                # Return all data needed for response
                return {
                    'id': subscription.id,
                    'user_email': subscription.user.email,
                    'user_username': subscription.user.username,
                    'plan_name': subscription.plan.name,
                    'plan_duration': subscription.plan.get_duration_display(),
                    'plan_price': float(subscription.plan.price),
                    'plan_credits': subscription.plan.credits,
                    'status': subscription.status,
                    'status_display': subscription.get_status_display(),
                    'start_date': subscription.start_date,
                    'end_date': subscription.end_date,
                    'credits_awarded': subscription.credits_awarded,
                    'is_auto_renewal': subscription.is_auto_renewal,
                    'payment_reference': subscription.payment_reference,
                    'days_remaining': subscription.days_remaining(),
                    'is_active_now': subscription.is_active(),
                    'created_at': subscription.created_at,
                    'updated_at': subscription.updated_at
                }, changes
        
        # Execute the update
        subscription_data, change_list = await perform_full_update()
        
        # Prepare response using the data from sync context
        subscription_response = UserSubscriptionResponse(**subscription_data)
        
        return UpdateSubscriptionStatusResponse(
            success=True,
            message=f"Subscription updated successfully. Changes: {', '.join(change_list) if change_list else 'No changes made'}",
            subscription=subscription_response
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating subscription: {str(e)}")


@router.delete("/delete_subscription/{subscription_id}")
async def delete_subscription(subscription_id: int):
    """Delete a subscription completely"""
    try:
        @sync_to_async
        def perform_deletion():
            try:
                subscription = UserSubscription.objects.get(id=subscription_id)
                
                # Store info for response before deletion
                user_email = subscription.user.email
                plan_name = subscription.plan.name
                
                # Delete the subscription
                subscription.delete()
                
                return user_email, plan_name
            except UserSubscription.DoesNotExist:
                return None, None
        
        # Execute the deletion
        user_email, plan_name = await perform_deletion()
        
        if user_email is None:
            raise HTTPException(status_code=404, detail=f"Subscription with ID {subscription_id} not found")
        
        return {
            "success": True,
            "message": f"Subscription '{plan_name}' for user '{user_email}' deleted successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting subscription: {str(e)}")






# ...existing code...
# (Remove the duplicate UpdateSubscriptionStatusResponse / ActiveSubscriptionResponse block if not needed above)
class ActiveSubscriptionResponse(BaseModel):
    success: bool
    message: str
    subscription: UserSubscriptionResponse




@router.get("/active_subscription/{username}", response_model=ActiveSubscriptionResponse)
async def get_active_subscription(username: str):
    """Get the most recent subscription for a user.
    Auto-expire ONLY when now >= end_date (strict). If status is 'expired' but end_date still future, reactivate.
    """
    try:
        try:
            user = await sync_to_async(HindAIUser.objects.get)(username=username)
        except HindAIUser.DoesNotExist:
            raise HTTPException(status_code=404, detail=f"User with username '{username}' not found")

        @sync_to_async
        def fetch_latest_data():
            now = timezone.now()
            sub = (UserSubscription.objects
                   .select_related('plan')
                   .filter(user=user)
                   .order_by('-id')
                   .first())
            if not sub:
                return None

            # Compute raw remaining (may be negative)
            if sub.end_date:
                delta = sub.end_date - now
                # days_remaining(): keep existing method if reliable, else fallback
                try:
                    calc_days = sub.days_remaining()
                except Exception:
                    calc_days = delta.days if delta.days >= 0 else 0
            else:
                calc_days = 0

            # If subscription marked expired but end_date still in future -> reactivate (was prematurely expired)
            if sub.end_date and sub.end_date > now and sub.status == 'expired':
                sub.status = 'active'
                sub.save(update_fields=['status', 'updated_at'])

            # Expire only when now >= end_date
            if sub.end_date and now >= sub.end_date and sub.status != 'expired':
                sub.status = 'expired'
                sub.save(update_fields=['status', 'updated_at'])
                calc_days = 0  # ensure 0 after expiry
            else:
                # Recalculate non-negative days (strict: if end_date in future delta.days + 1 maybe? keep method result but clamp >=0)
                if sub.end_date:
                    # Recompute to avoid stale after status changes
                    remaining_days = (sub.end_date.date() - now.date()).days
                    calc_days = max(remaining_days, 0)
                else:
                    calc_days = 0

            data = {
                'id': sub.id,
                'user_email': sub.user.email,
                'user_username': sub.user.username,
                'plan_name': sub.plan.name,
                'plan_duration': sub.plan.get_duration_display(),
                'plan_price': float(sub.plan.price),
                'plan_credits': sub.plan.credits,
                'status': sub.status,
                'status_display': sub.get_status_display(),
                'start_date': sub.start_date,
                'end_date': sub.end_date,
                'credits_awarded': sub.credits_awarded,
                'is_auto_renewal': sub.is_auto_renewal,
                'payment_reference': sub.payment_reference,
                'days_remaining': calc_days,
                'is_active_now': (sub.status == 'active' and calc_days > 0),
                'created_at': sub.created_at,
                'updated_at': sub.updated_at
            }
            return data

        subscription_data = await fetch_latest_data()

        if not subscription_data:
            raise HTTPException(status_code=404, detail=f"No subscription found for user '{username}'")

        subscription_response = UserSubscriptionResponse(**subscription_data)

        return ActiveSubscriptionResponse(
            success=True,
            message=f"Latest subscription (status={subscription_response.status}) retrieved for user '{username}'",
            subscription=subscription_response
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving subscription: {str(e)}")