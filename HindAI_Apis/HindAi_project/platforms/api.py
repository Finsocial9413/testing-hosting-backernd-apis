from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Union, Optional
from django.contrib.auth import get_user_model
from asgiref.sync import sync_to_async
from .models import AvailablePlatforms, UserConnect
from django.db import IntegrityError


router = APIRouter()


class Platform(BaseModel):
    name: str
    icon: str
    access_link: str
    
class UserPlatformConnection(BaseModel):
    user: str
    platform: str
    model_name: list[str]
    api_key: str

class UpdateConnection(BaseModel):
    api_key: Optional[str] = None
    model_name: Optional[list[str]] = None

class UpdateAPIKey(BaseModel):
    api_key: str

class UpdateModels(BaseModel):
    model_name: list[str]


@router.get("/platforms", response_model=List[Platform])
async def get_platform_details():
    """
    Get all platform details
    """
    try:
        platforms = await sync_to_async(list)(AvailablePlatforms.objects.all())
        
        return [Platform(
            name=platform.platform_name,
            icon=platform.icon,
            access_link=platform.access_link if platform.access_link else ''
        ) for platform in platforms]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting platform details: {str(e)}")


@router.post("/connect")
async def connect_user_to_platform(connection: UserPlatformConnection):
    """
    Connect a user to a platform with the specified models and API key
    """
    try:
        User = get_user_model()
        user = await sync_to_async(User.objects.get)(username=connection.user)
        platform = await sync_to_async(AvailablePlatforms.objects.get)(platform_name=connection.platform)
        
        models_str = ", ".join(connection.model_name)
        
        user_connection, created = await sync_to_async(UserConnect.objects.update_or_create)(
            user=user,
            platform=platform,
            defaults={
                'api_key': connection.api_key, 
                'model_name': models_str,
                'is_active': True
            }
        )
        
        action = "created" if created else "updated"
        
        return {
            "user": user.username,
            "platform": platform.platform_name,
            "model_name": connection.model_name,
            "api_key": connection.api_key,
            "message": f"Successfully {action} connection to {platform.platform_name}"
        }
    except User.DoesNotExist:
        raise HTTPException(status_code=404, detail="User not found")
    except AvailablePlatforms.DoesNotExist:
        raise HTTPException(status_code=404, detail="Platform not found")
    except IntegrityError:
        raise HTTPException(status_code=400, detail="User already connected to this platform")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error connecting user to platform: {str(e)}")


@router.get("/user-connections/{username}", response_model=List[UserPlatformConnection])
async def get_user_connections(username: str):
    """
    Get all platform connections for a specific user
    """
    try:
        User = get_user_model()
        user = await sync_to_async(User.objects.get)(username=username)
        
        connections = await sync_to_async(list)(
            UserConnect.objects.filter(user=user).select_related('platform')
        )
        
        return [
            UserPlatformConnection(
                user=user.username,
                platform=connection.platform.platform_name,
                model_name=connection.model_name.split(", ") if connection.model_name else [],
                api_key=connection.api_key
            ) for connection in connections
        ]
    except User.DoesNotExist:
        raise HTTPException(status_code=404, detail="User not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting user connections: {str(e)}")


@router.put("/update-connection/{username}/{platform_name}")
async def update_user_connection(username: str, platform_name: str, update_data: UpdateConnection):
    """
    Update API key and/or models for a specific user's platform connection
    """
    try:
        User = get_user_model()
        user = await sync_to_async(User.objects.get)(username=username)
        platform = await sync_to_async(AvailablePlatforms.objects.get)(platform_name=platform_name)
        
        connection = await sync_to_async(UserConnect.objects.get)(user=user, platform=platform)
        
        if update_data.api_key is not None:
            connection.api_key = update_data.api_key
        
        if update_data.model_name is not None:
            connection.model_name = ", ".join(update_data.model_name)
        
        await sync_to_async(connection.save)()
        
        return {
            "user": user.username,
            "platform": platform.platform_name,
            "model_name": connection.model_name.split(", ") if connection.model_name else [],
            "api_key": connection.api_key,
            "message": f"Successfully updated connection to {platform.platform_name}"
        }
    except User.DoesNotExist:
        raise HTTPException(status_code=404, detail="User not found")
    except AvailablePlatforms.DoesNotExist:
        raise HTTPException(status_code=404, detail="Platform not found")
    except UserConnect.DoesNotExist:
        raise HTTPException(status_code=404, detail="Connection not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating connection: {str(e)}")


@router.put("/update-api-key/{username}/{platform_name}")
async def update_api_key(username: str, platform_name: str, update_data: UpdateAPIKey):
    """
    Update only the API key for a specific user's platform connection
    """
    try:
        User = get_user_model()
        user = await sync_to_async(User.objects.get)(username=username)
        platform = await sync_to_async(AvailablePlatforms.objects.get)(platform_name=platform_name)
        
        connection = await sync_to_async(UserConnect.objects.get)(user=user, platform=platform)
        connection.api_key = update_data.api_key
        await sync_to_async(connection.save)()
        
        return {
            "user": user.username,
            "platform": platform.platform_name,
            "api_key": connection.api_key,
            "message": f"Successfully updated API key for {platform.platform_name}"
        }
    except User.DoesNotExist:
        raise HTTPException(status_code=404, detail="User not found")
    except AvailablePlatforms.DoesNotExist:
        raise HTTPException(status_code=404, detail="Platform not found")
    except UserConnect.DoesNotExist:
        raise HTTPException(status_code=404, detail="Connection not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating API key: {str(e)}")


@router.put("/update-models/{username}/{platform_name}")
async def update_models(username: str, platform_name: str, update_data: UpdateModels):
    """
    Update only the models for a specific user's platform connection
    """
    try:
        User = get_user_model()
        user = await sync_to_async(User.objects.get)(username=username)
        platform = await sync_to_async(AvailablePlatforms.objects.get)(platform_name=platform_name)
        
        connection = await sync_to_async(UserConnect.objects.get)(user=user, platform=platform)
        connection.model_name = ", ".join(update_data.model_name)
        await sync_to_async(connection.save)()
        
        return {
            "user": user.username,
            "platform": platform.platform_name,
            "model_name": update_data.model_name,
            "message": f"Successfully updated models for {platform.platform_name}"
        }
    except User.DoesNotExist:
        raise HTTPException(status_code=404, detail="User not found")
    except AvailablePlatforms.DoesNotExist:
        raise HTTPException(status_code=404, detail="Platform not found")
    except UserConnect.DoesNotExist:
        raise HTTPException(status_code=404, detail="Connection not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating models: {str(e)}")


@router.delete("/delete-connection/{username}/{platform_name}")
async def delete_user_connection(username: str, platform_name: str):
    """
    Delete a specific platform connection for a user
    """
    try:
        User = get_user_model()
        user = await sync_to_async(User.objects.get)(username=username)
        platform = await sync_to_async(AvailablePlatforms.objects.get)(platform_name=platform_name)
        
        connection = await sync_to_async(UserConnect.objects.get)(user=user, platform=platform)
        await sync_to_async(connection.delete)()
        
        return {
            "message": f"Successfully deleted connection between {username} and {platform_name}"
        }
    except User.DoesNotExist:
        raise HTTPException(status_code=404, detail="User not found")
    except AvailablePlatforms.DoesNotExist:
        raise HTTPException(status_code=404, detail="Platform not found")
    except UserConnect.DoesNotExist:
        raise HTTPException(status_code=404, detail="Connection not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting connection: {str(e)}")


@router.delete("/delete-all-connections/{username}")
async def delete_all_user_connections(username: str):
    """
    Delete all platform connections for a user
    """
    try:
        User = get_user_model()
        user = await sync_to_async(User.objects.get)(username=username)
        
        connections_count = await sync_to_async(UserConnect.objects.filter(user=user).count)()
        await sync_to_async(UserConnect.objects.filter(user=user).delete)()
        
        return {
            "message": f"Successfully deleted {connections_count} connections for user {username}"
        }
    except User.DoesNotExist:
        raise HTTPException(status_code=404, detail="User not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting all connections: {str(e)}")