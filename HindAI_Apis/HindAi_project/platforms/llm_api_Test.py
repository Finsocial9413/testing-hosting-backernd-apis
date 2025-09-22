import os
import sys
import pathlib
import django
from fastapi import APIRouter, HTTPException, Depends
from fastapi import FastAPI  # NEW
from agno.agent import Agent
from agno.models.openai import OpenAIChat



from pydantic import BaseModel
import asyncio
from asgiref.sync import sync_to_async
# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# Robustly add the project root (folder that has manage.py) to sys.path
PROJECT_ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'HindAi_project.settings')
django.setup()
from platforms.models import UserConnect,PlatformModel,AvailablePlatforms
from HindAi_users.models import HindAIUser
from small_codes.api_test import test as api_Test
router = APIRouter()

# FastAPI application (so uvicorn platforms.llm_api_Test:app works)
app = FastAPI()
app.include_router(router, prefix="/platforms", tags=["platforms"])

class test(BaseModel):
    platform_name: str
    api: str

@router.post("/test")
async def create_test(test: test):
    """
    Create a new test instance.
    """
    valid = api_Test(test.platform_name, test.api)
    if valid == 'not working' or valid=='yes':
        return {'Api Valid': valid}
    else:
        return valid



@router.get("/test/{platform_name}")
async def get_test(platform_name: str):
    """
    Get the test instance for a specific platform.
    """
    try:
        platform_obj = await sync_to_async(AvailablePlatforms.objects.get)(platform_name=platform_name)
    except AvailablePlatforms.DoesNotExist:
        raise HTTPException(status_code=404, detail="Platform not found")

    platform_models = await sync_to_async(list)(PlatformModel.objects.filter(platform=platform_obj))

    if not platform_models:
        return {"platform_name": platform_name, "items": []}

    # Try common possible field names; fall back to primary key
    items = []
    for m in platform_models:
        display_name = (
             f"{m.model}"
        )
        api_value = getattr(m, "id", None)
        items.append({"name": display_name, "id": api_value})
    return {"platform_name": platform_name, "items": items}




@router.get("/user-platforms/{username}")
async def get_user_platform_models(username: str):
    """
    Return all platforms a user is connected to with:
      platform_name, api_key, models list (parsed from UserConnect.model_name),
      and available_platform_models (all active models defined for that platform).
    """
    try:
        user = await sync_to_async(HindAIUser.objects.get)(username=username)
    except HindAIUser.DoesNotExist:
        raise HTTPException(status_code=404, detail="User not found")

    connections = await sync_to_async(list)(
        UserConnect.objects.select_related("platform").filter(user=user, is_active=True)
    )

    if not connections:
        return {"username": username, "platforms": []}

    result = []
    for uc in connections:
        # Parse the stored model_name field into a list (handles comma / newline separated)
        raw = uc.model_name or ""
        user_models = [
            m.strip() for m in raw.replace("\n", ",").split(",") if m.strip()
        ]

      

        result.append({
            "platform_name": uc.platform.platform_name,
            "api_key": uc.api_key,
            "models": user_models,
        })

    return {"username": username, "platforms": result}



