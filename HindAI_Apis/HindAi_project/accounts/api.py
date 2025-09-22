from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from HindAi_users.models import HindAIUser as User
from django.shortcuts import get_object_or_404
from asgiref.sync import sync_to_async
from .models import SnaptradeUsers
from .code_snippts.account_Create import register_snaptrade_user
from .code_snippts.delete_user import delete_snaptrade_user_data
from .code_snippts.update_Secret import update_snaptrade_secret
from .code_snippts.get_account_Details import account_details_Tools
router = APIRouter()

# Pydantic models for request/response
class SnaptradeUserCreate(BaseModel):
    username: str


class SnaptradeUserUpdate(BaseModel):
    userId: Optional[str] = None
    userSecret: Optional[str] = None
class SnaptradeUserAccountDetails(BaseModel):
    accountDetails: dict

class SnaptradeUserResponse(BaseModel):
    id: int
    username: str
    userId: str
    userSecret: Optional[str] = None
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True

@router.get("/", response_model=List[SnaptradeUserResponse])
async def list_snaptrade_users():
    """Get all Snaptrade users"""
    users = await sync_to_async(list)(SnaptradeUsers.objects.select_related('user').all())
    return [
        SnaptradeUserResponse(
            id=user.id,
            username=user.user.username,
            userId=user.userId,
            created_at=user.created_at.isoformat(),
            updated_at=user.updated_at.isoformat()
        )
        for user in users
    ]


@router.post("/", response_model=SnaptradeUserResponse)
async def create_snaptrade_user(user_data: SnaptradeUserCreate):
    """Create a new Snaptrade user"""
    try:
        # Get or create Django user
        # creating user 
        created_user_response = await sync_to_async(register_snaptrade_user)(user_data.username)
        
        # Extract data from API response object
        created_user = created_user_response.body if hasattr(created_user_response, 'body') else created_user_response
        
        django_user, created = await sync_to_async(User.objects.get_or_create)(
            username=user_data.username,
            defaults={'email': f"{user_data.username}@example.com"}
        )
        # Create Snaptrade user
        snaptrade_user = await sync_to_async(SnaptradeUsers.objects.create)(
            user=django_user,
            userId=created_user.get('userId') or getattr(created_user, 'user_id', ''),
            userSecret=created_user.get('userSecret') or getattr(created_user, 'user_secret', '')
        )
        
        
        return SnaptradeUserResponse(
            id=snaptrade_user.id,
            username=snaptrade_user.user.username,
            userId=snaptrade_user.userId,
            userSecret=snaptrade_user.userSecret,
            created_at=snaptrade_user.created_at.isoformat(),
            updated_at=snaptrade_user.updated_at.isoformat()
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/{username}", response_model=SnaptradeUserResponse)
async def update_snaptrade_user_secret(username: str):
    """Update a Snaptrade user"""
    try:
        # Get the user object properly
        snaptrade_user = await sync_to_async(SnaptradeUsers.objects.select_related('user').get)(user__username=username)

        update_info = update_snaptrade_secret(username, snaptrade_user.userSecret)
        
        # Update the userSecret field
        snaptrade_user.userSecret = update_info.body['userSecret']
        await sync_to_async(snaptrade_user.save)()
        # For now, just return the current user data
        # You can add update logic here as needed
        return SnaptradeUserResponse(
            id=snaptrade_user.id,
            username=snaptrade_user.user.username,
            userId=snaptrade_user.userId,
            userSecret=update_info.body['userSecret'],
            created_at=snaptrade_user.created_at.isoformat(),
            updated_at=snaptrade_user.updated_at.isoformat()
        )
  
    except SnaptradeUsers.DoesNotExist:
        raise HTTPException(status_code=404, detail="Snaptrade user not found")



@router.delete("/{username}")
async def delete_snaptrade_user(username: str):
    """Delete a Snaptrade user"""
    try:
        delete_user = delete_snaptrade_user_data(username)
        print(f"Delete user response: {delete_user}")
        snaptrade_user = await sync_to_async(SnaptradeUsers.objects.get)(user__username=username)
        await sync_to_async(snaptrade_user.delete)()
        return {"message": "Snaptrade user deleted successfully"}
    except SnaptradeUsers.DoesNotExist:
        raise HTTPException(status_code=404, detail="Snaptrade user not found")

@router.get("/by-username/{username}", response_model=SnaptradeUserResponse)
async def get_snaptrade_user_by_username(username: str):
    """Get Snaptrade user by Django username"""
    try:
        user = await sync_to_async(SnaptradeUsers.objects.select_related('user').get)(user__username=username)
        return SnaptradeUserResponse(
            id=user.id,
            username=user.user.username,
            userId=user.userId,
            created_at=user.created_at.isoformat(),
            updated_at=user.updated_at.isoformat()
        )
    except SnaptradeUsers.DoesNotExist:
        raise HTTPException(status_code=404, detail="Snaptrade user not found")

    except SnaptradeUsers.DoesNotExist:
        raise HTTPException(status_code=404, detail="Snaptrade user not found")


@router.get("/account-details/{username}", response_model=SnaptradeUserAccountDetails)
async def get_account_details(username: str):
    """Get Snaptrade account details by username"""
    try:
        user = await sync_to_async(SnaptradeUsers.objects.select_related('user').get)(user__username=username)
        account_details = account_details_Tools(user.userId, user.userSecret)
        data = {'accountDetails': account_details}
        return SnaptradeUserAccountDetails(
            accountDetails=data
        )
    except SnaptradeUsers.DoesNotExist:
        raise HTTPException(status_code=404, detail="Snaptrade user not found")
