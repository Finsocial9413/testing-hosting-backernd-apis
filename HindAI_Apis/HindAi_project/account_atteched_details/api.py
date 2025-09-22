from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from HindAi_users.models import HindAIUser as User
from django.shortcuts import get_object_or_404
from asgiref.sync import sync_to_async
from .models import AccountAttachedDetail
from accounts.models import SnaptradeUsers
from .code_snippts.atteched_Account_Details import get_all_accounts_details
from .code_snippts.delete_Speacific_Connection import delete_Specific_Connection
from .code_snippts.get_atteched_account_bank_bakance import get_user_account_balance
import logging

router = APIRouter()

# Pydantic models
class UsernameRequest(BaseModel):
    username: str

class AccountDetailResponse(BaseModel):
    user_id: str
    accounts_found: int
    accounts_saved: int
    message: str

class CurrencyInfo(BaseModel):
    code: str
    name: str
    id: str

class BalanceData(BaseModel):
    currency: CurrencyInfo
    cash: float
    buying_power: float

class AccountBalanceResponse(BaseModel):
    user_id: str
    account_id: str
    platform_name: str
    balance_data: List[BalanceData]  # Changed from dict to List[BalanceData]
    message: str

@router.post("/sync-user-accounts/", response_model=AccountDetailResponse)
async def sync_user_accounts(request: UsernameRequest):
    """
    Sync user accounts from SnapTrade API and save to AccountAttachedDetail model
    
    Args:
        request: Contains username to lookup
    
    Returns:
        AccountDetailResponse with sync results
    """
    try:
        # Get Django user by username
        user = await sync_to_async(get_object_or_404)(User, username=request.username)
        
        # Get SnapTrade user credentials
        try:
            snaptrade_user = await sync_to_async(lambda: user.snaptrade_user)()
        except SnaptradeUsers.DoesNotExist:
            raise HTTPException(
                status_code=404, 
                detail=f"SnapTrade credentials not found for user: {request.username}"
            )
        
        # Get all account details from SnapTrade API
        accounts_data = await sync_to_async(get_all_accounts_details)(
            snaptrade_user.userId, 
            snaptrade_user.userSecret
        )
        
        if not accounts_data:
            return AccountDetailResponse(
                user_id=str(user.id),
                accounts_found=0,
                accounts_saved=0,
                message="No accounts found for this user"
            )
        
        accounts_saved = 0
        
        # Process each account and save to database
        for account_data in accounts_data:
            try:
                # Extract account information
                account_id = account_data.get('id', '')
                platform_name = account_data.get('institution_name', 'Unknown')
                brokerage_authorization = ''
                
                # Extract brokerage authorization
                if 'brokerage_authorization' in account_data:
                    brokerage_auth = account_data['brokerage_authorization']
                    if isinstance(brokerage_auth, dict):
                        # Try to get the authorization ID
                        brokerage_authorization = brokerage_auth.get('id', '') or brokerage_auth.get('authorization_id', '')
                        
                        # If institution_name is not available, try to get from brokerage_authorization
                        if platform_name == 'Unknown' and 'brokerage' in brokerage_auth and isinstance(brokerage_auth['brokerage'], dict):
                            platform_name = brokerage_auth['brokerage'].get('name', 'Unknown')
                    else:
                        # If brokerage_authorization is a string (ID)
                        brokerage_authorization = str(brokerage_auth)
                
                if not account_id:
                    continue
                
                # Create or update AccountAttachedDetail
                account_detail, created = await sync_to_async(AccountAttachedDetail.objects.get_or_create)(
                    user=user,
                    platform_name=platform_name,
                    account_id=account_id,
                    defaults={
                        'brokerage_authorization': brokerage_authorization,
                        'is_active': True
                    }
                )
                
                # If account already exists, update it
                if not created:
                    account_detail.brokerage_authorization = brokerage_authorization
                    account_detail.is_active = True
                    await sync_to_async(account_detail.save)()
                
                accounts_saved += 1
                
            except Exception as e:
                logging.error(f"Error saving account {account_data.get('id', 'unknown')}: {e}")
                continue
        
        return AccountDetailResponse(
            user_id=str(user.id),
            accounts_found=len(accounts_data),
            accounts_saved=accounts_saved,
            message=f"Successfully synced {accounts_saved} out of {len(accounts_data)} accounts"
        )
        
    except User.DoesNotExist:
        raise HTTPException(
            status_code=404, 
            detail=f"User not found: {request.username}"
        )
    except Exception as e:
        logging.error(f"Error syncing accounts for user {request.username}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@router.get("/user-attached-accounts/{username}/", response_model=List[dict])
async def get_user_attached_accounts(username: str):
    """
    Get all attached accounts for a user from the database
    
    Args:
        username: Username to lookup
    
    Returns:
        List of attached accounts
    """
    try:
        user = await sync_to_async(get_object_or_404)(User, username=username)
        
        # Get all attached accounts for the user
        attached_accounts = await sync_to_async(list)(
            AccountAttachedDetail.objects.filter(user=user).values(
                'id', 'platform_name', 'account_id', 'brokerage_authorization', 'is_active', 
                'connected_at', 'updated_at'
            )
        )
        
        return attached_accounts
        
    except User.DoesNotExist:
        raise HTTPException(
            status_code=404, 
            detail=f"User not found: {username}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving attached accounts: {str(e)}"
        )

@router.delete("/deactivate-account/{username}/{account_id}/")
async def deactivate_attached_account(username: str, account_id: str):
    """
    Deactivate a specific attached account and delete it from broker side
    
    Args:
        username: Username
        account_id: Account ID to deactivate
    
    Returns:
        Success message
    """
    try:
        user = await sync_to_async(get_object_or_404)(User, username=username)
        
        # Get the account detail to deactivate
        account_detail = await sync_to_async(get_object_or_404)(
            AccountAttachedDetail, 
            user=user, 
            account_id=account_id
        )
        
        # Get SnapTrade user credentials
        try:
            snaptrade_user = await sync_to_async(lambda: user.snaptrade_user)()
        except SnaptradeUsers.DoesNotExist:
            raise HTTPException(
                status_code=404, 
                detail=f"SnapTrade credentials not found for user: {username}"
            )
        
        # If we have brokerage authorization ID, try to delete it from broker side
        broker_deletion_success = False
        if account_detail.brokerage_authorization:
            try:
                # Delete the connection from broker side using the brokerage authorization ID
                result = await sync_to_async(delete_Specific_Connection)(
                    snaptrade_user.userId,
                    snaptrade_user.userSecret,
                    account_detail.brokerage_authorization
                )
                
                if result is not None:
                    broker_deletion_success = True
                    logging.info(f"Successfully deleted broker connection for account {account_id}")
                else:
                    logging.warning(f"Failed to delete broker connection for account {account_id}")
                    
            except Exception as e:
                logging.error(f"Error deleting broker connection for account {account_id}: {e}")
        
        # Deactivate the account in our database regardless of broker deletion result
        account_detail.is_active = False
        await sync_to_async(account_detail.save)()
        
        # Prepare response message based on results
        if account_detail.brokerage_authorization:
            if broker_deletion_success:
                message = f"Account {account_id} deactivated successfully and removed from broker"
            else:
                message = f"Account {account_id} deactivated in database, but failed to remove from broker"
        else:
            message = f"Account {account_id} deactivated successfully (no brokerage authorization found)"
        
        return {
            "message": message,
            "account_id": account_id,
            "database_deactivated": True,
            "broker_deleted": broker_deletion_success,
            "brokerage_authorization": account_detail.brokerage_authorization or "Not available"
        }
        
    except (User.DoesNotExist, AccountAttachedDetail.DoesNotExist):
        raise HTTPException(
            status_code=404, 
            detail="User or attached account not found"
        )
    except Exception as e:
        logging.error(f"Error deactivating account {account_id} for user {username}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error deactivating account: {str(e)}"
        )

@router.get("/account-balance/{username}/{account_id}/", response_model=AccountBalanceResponse)
async def get_account_balance(username: str, account_id: str):
    """
    Get account balance for a specific attached account
    
    Args:
        username: Username to lookup
        account_id: Account ID to get balance for
    
    Returns:
        AccountBalanceResponse with balance information
    """
    try:
        user = await sync_to_async(get_object_or_404)(User, username=username)
        
        # Get the account detail to verify it exists and is active
        account_detail = await sync_to_async(get_object_or_404)(
            AccountAttachedDetail, 
            user=user, 
            account_id=account_id,
            is_active=True
        )
        
        # Get SnapTrade user credentials
        try:
            snaptrade_user = await sync_to_async(lambda: user.snaptrade_user)()
        except SnaptradeUsers.DoesNotExist:
            raise HTTPException(
                status_code=404, 
                detail=f"SnapTrade credentials not found for user: {username}"
            )
        
        # Get account balance from SnapTrade API
        try:
            balance_data = await sync_to_async(get_user_account_balance)(
                account_id=account_id,
                user_id=snaptrade_user.userId,
                user_secret=snaptrade_user.userSecret
            )
            
            return AccountBalanceResponse(
                user_id=str(user.id),
                account_id=account_id,
                platform_name=account_detail.platform_name,
                balance_data=balance_data,  # This should now work as it's a list
                message="Account balance retrieved successfully"
            )
            
        except Exception as e:
            logging.error(f"Error retrieving balance for account {account_id}: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Error retrieving account balance from SnapTrade API: {str(e)}"
            )
        
    except (User.DoesNotExist, AccountAttachedDetail.DoesNotExist):
        raise HTTPException(
            status_code=404, 
            detail="User not found or account not attached/active for this user"
        )
    except Exception as e:
        logging.error(f"Error getting account balance for user {username}, account {account_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )




