


from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional

from HindAi_users.models import HindAIUser as User
from django.shortcuts import get_object_or_404
from asgiref.sync import sync_to_async
from .code_snippts.connection_portal import connection_portal
from .code_snippts.get_speacfic_authorization_id import get_specific_broker_details
from .code_snippts.get_speacific_Connection_Details import get_speacific_connection_details
# from .code_snippts.accounts_holdings import user_holdings_data
from .code_snippts.get_all_positions import get_All_positions
from .code_snippts.list_options_positions import get_All_options_positions
from .code_snippts.list_Account_Activity import list_of_Account_Activity
from .code_snippts.delete_All_connections import delete_all_connections_complete
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(os.path.abspath(__file__))))))

from accounts.models import SnaptradeUsers

router = APIRouter()


class SnaptradeUserlistofUsers_accounts(BaseModel):
    account_list_Details: list  # Changed from dict to list
    
class SnaptradeUserlistof_All_broker_authorization(BaseModel):
    broker_Authorization: dict  # Changed from dict to list
    
class SnaptradeUser_Connecting_platform(BaseModel):
    connecting_Details: dict  # Changed from dict to list
    
    
class SnaptradeUser_Connecting_platform_balances(BaseModel):
    connecting_account_balance: list  # Changed from dict to list



@router.get("/connect-portal/{username}", response_model=SnaptradeUser_Connecting_platform)
async def connect_portal(username: str):
    try:
        user = await sync_to_async(SnaptradeUsers.objects.select_related('user').get)(user__username=username)
        connect =  connection_portal(user.userId, user.userSecret)

        return SnaptradeUser_Connecting_platform(
            connecting_Details=connect
        )
    except SnaptradeUsers.DoesNotExist:
        raise HTTPException(status_code=404, detail="Snaptrade user not found")
    
    






@router.get("/get_specific_connection_details/{username}/{institution_name}", response_model=dict)
async def get_specific_connection_details(username: str, institution_name: str):
    """
    Get specific connection details for a given institution name

    Args:
        user_id (str): User ID for the SnapTrade user
        user_secret (str): User secret for the SnapTrade user
        institution_name (str): Name of the brokerage institution to get details for

    Returns:
        dict: Connection details for the specified institution name
    """
    
    try:
        user = await sync_to_async(SnaptradeUsers.objects.select_related('user').get)(user__username=username)
        broker_details = get_specific_broker_details(user.userId, user.userSecret, institution_name)

        get_authorization = broker_details['brokerage_authorization']
        # print(f"Authorization ID: {get_authorization}")

        response = get_speacific_connection_details(
            user_id=user.userId,
            user_secret=user.userSecret,
            authorization_id=get_authorization
        )
        
        return response
    
    except Exception as e:
        print(f"Error getting specific connection details: {e}")
        return None 
    
    
# @router.get("/get_user_holdings/{username}", response_model=dict)
# async def get_user_holdings(username: str):
#     try:
#         user = await sync_to_async(SnaptradeUsers.objects.select_related('user').get)(user__username=username)
#         holdings = user_holdings_data(user.userId, user.userSecret)
#         return {"holdings": holdings}
#     except SnaptradeUsers.DoesNotExist:
#         raise HTTPException(status_code=404, detail="Snaptrade user not found")
    
    
@router.get("/list-all-connections/{username}", response_model=dict)
async def list_all_connections_endpoint(username: str):
    """
    List all brokerage connections for a specific user

    Args:
        username (str): Username of the SnapTrade user

    Returns:
        dict: Summary statistics and raw connection data
    """
    
    try:
        user = await sync_to_async(SnaptradeUsers.objects.select_related('user').get)(user__username=username)
        connections = list_all_connections(user.userId, user.userSecret)
        
        if connections is not None:
            return {"connections": connections}
        else:
            return {"error": "Failed to retrieve brokerage connections"}
    
    except SnaptradeUsers.DoesNotExist:
        raise HTTPException(status_code=404, detail="Snaptrade user not found")
    
    
@router.get("/get-all-positions/{username}", response_model=dict)
async def get_all_positions_endpoint(username: str):
    try:
        user = await sync_to_async(SnaptradeUsers.objects.select_related('user').get)(user__username=username)
        positions = get_All_positions(user.userId, user.userSecret)
        return {"positions": positions}
    except SnaptradeUsers.DoesNotExist:
        raise HTTPException(status_code=404, detail="Snaptrade user not found")
    except Exception as e:
        print(f"Error retrieving positions: {e}")
        return {"error": "Failed to retrieve positions"}
    
    
@router.get("/get-all-options-positions/{username}", response_model=dict)
async def get_all_options_positions_endpoint(username: str):
    try:
        user = await sync_to_async(SnaptradeUsers.objects.select_related('user').get)(user__username=username)
        options_positions = get_All_options_positions(user.userId, user.userSecret)
        return {"options_positions": options_positions}
    except SnaptradeUsers.DoesNotExist:
        raise HTTPException(status_code=404, detail="Snaptrade user not found")
    except Exception as e:
        print(f"Error retrieving options positions: {e}")
        return {"error": "Failed to retrieve options positions"}
    
    
@router.get("/list-account-activity/{username}/{account_id}", response_model=dict)
async def list_account_activity(username: str, account_id: str, start_date: Optional[str] = None, end_date: Optional[str] = None, offset: int = 0, limit: int = 1000):
    try:
        user = await sync_to_async(SnaptradeUsers.objects.select_related('user').get)(user__username=username)
        account_activity = list_of_Account_Activity(
            user_id=user.userId,
            user_secret=user.userSecret,
            account_id=account_id,
            start_date=start_date,
            end_date=end_date,
            offset=offset,
            limit=limit
        )
        return {"account_activity": account_activity}
    except SnaptradeUsers.DoesNotExist:
        raise HTTPException(status_code=404, detail="Snaptrade user not found")
    except Exception as e:
        print(f"Error retrieving account activity: {e}")
        return {"error": "Failed to retrieve account activity"}
    

@router.get("/delete-all-connections/{username}", response_model=dict)
async def delete_all_connections_endpoint(username: str):
    """
    Delete all brokerage connections for a specific user

    Args:
        username (str): Username of the SnapTrade user

    Returns:
        dict: Summary of deleted connections
    """
    
    try:
        user = await sync_to_async(SnaptradeUsers.objects.select_related('user').get)(user__username=username)
        result = delete_all_connections_complete(user.userId, user.userSecret)
        
        if result:
            return result
        else:
            return {"error": "No connections found or deletion failed."}
    
    except SnaptradeUsers.DoesNotExist:
        raise HTTPException(status_code=404, detail="Snaptrade user not found")


