from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Union, Optional
from django.contrib.auth import get_user_model
from asgiref.sync import sync_to_async
from .models import SubscriptionPlan
from django.db import IntegrityError
from decimal import Decimal
from datetime import datetime

router = APIRouter()

class SubscriptionPlanResponse(BaseModel):
    id: int
    plan_name: str
    plan_price: float
    plan_duration: str
    plan_duration_display: str
    plans_credits: int
    plans_features: List[str]  # Changed to list for better structure
    plans_status: bool
    plans_popularity: bool
    created_at: datetime
    updated_at: datetime
    duration_in_days: int

class SubscriptionPlansListResponse(BaseModel):
    plans: List[SubscriptionPlanResponse]
    total_count: int

@router.get("/subscription_plans", response_model=SubscriptionPlansListResponse)
async def get_subscription_plans():
    """Get all subscription plans"""
    try:
        # Get all subscription plans
        plans = await sync_to_async(list)(SubscriptionPlan.objects.all())
        
        # Convert to response format
        plan_responses = []
        for plan in plans:
            plan_response = SubscriptionPlanResponse(
                id=plan.id,
                plan_name=plan.name,
                plan_price=float(plan.price),
                plan_duration=plan.duration,
                plan_duration_display=plan.get_duration_display(),
                plans_credits=plan.credits,
                plans_features=plan.get_features_list(),
                plans_status=plan.is_active,
                plans_popularity=plan.is_popular,
                created_at=plan.created_at,
                updated_at=plan.updated_at,
                duration_in_days=plan.get_duration_in_days()
            )
            plan_responses.append(plan_response)
        
        return SubscriptionPlansListResponse(
            plans=plan_responses,
            total_count=len(plan_responses)
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching subscription plans: {str(e)}")

@router.get("/subscription_plans/active", response_model=SubscriptionPlansListResponse)
async def get_active_subscription_plans():
    """Get only active subscription plans"""
    try:
        # Get only active subscription plans
        plans = await sync_to_async(list)(SubscriptionPlan.objects.filter(is_active=True))
        
        # Convert to response format
        plan_responses = []
        for plan in plans:
            plan_response = SubscriptionPlanResponse(
                id=plan.id,
                plan_name=plan.name,
                plan_price=float(plan.price),
                plan_duration=plan.duration,
                plan_duration_display=plan.get_duration_display(),
                plans_credits=plan.credits,
                plans_features=plan.get_features_list(),
                plans_status=plan.is_active,
                plans_popularity=plan.is_popular,
                created_at=plan.created_at,
                updated_at=plan.updated_at,
                duration_in_days=plan.get_duration_in_days()
            )
            plan_responses.append(plan_response)
        
        return SubscriptionPlansListResponse(
            plans=plan_responses,
            total_count=len(plan_responses)
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching active subscription plans: {str(e)}")

@router.get("/subscription_plans/{plan_id}", response_model=SubscriptionPlanResponse)
async def get_subscription_plan_by_id(plan_id: int):
    """Get a specific subscription plan by ID"""
    try:
        # Get specific plan
        plan = await sync_to_async(SubscriptionPlan.objects.get)(id=plan_id)
        
        return SubscriptionPlanResponse(
            id=plan.id,
            plan_name=plan.name,
            plan_price=float(plan.price),
            plan_duration=plan.duration,
            plan_duration_display=plan.get_duration_display(),
            plans_credits=plan.credits,
            plans_features=plan.get_features_list(),
            plans_status=plan.is_active,
            plans_popularity=plan.is_popular,
            created_at=plan.created_at,
            updated_at=plan.updated_at,
            duration_in_days=plan.get_duration_in_days()
        )
    
    except SubscriptionPlan.DoesNotExist:
        raise HTTPException(status_code=404, detail="Subscription plan not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching subscription plan: {str(e)}")


