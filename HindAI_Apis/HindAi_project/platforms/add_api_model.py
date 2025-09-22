import os
import sys
import django

from fastapi import HTTPException, APIRouter, status
from asgiref.sync import sync_to_async
from django.db import IntegrityError
from pydantic import BaseModel

# Path + Django setup
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'HindAi_project.settings')
django.setup()

from platforms.models import PlatformModel, AvailablePlatforms  # noqa
from small_codes.model_update_workflow import test_Tool_bro
router = APIRouter()

# Input schema
class PlatformModelIn(BaseModel):
    platform_name: str
    model_name: str
    support: bool
    is_active: bool

# Output schema
class PlatformModelOut(BaseModel):
    id: int
    platform_name: str
    model_name: str
    support: bool
    is_active: bool

@sync_to_async
def _create_platform_model(data: PlatformModelIn):
    try:
        # Resolve platform
        try:
            platform = AvailablePlatforms.objects.get(platform_name=data.platform_name)
        except AvailablePlatforms.DoesNotExist:
            raise HTTPException(status_code=404, detail=f"Platform '{data.platform_name}' not found")
        # supp = test_Tool_bro(data.model_name)

        obj = PlatformModel.objects.create(
            platform=platform,
            model=data.model_name,
            support=data.support,
            is_active=data.is_active
        )
        return obj
    except IntegrityError:
        # Unique constraint (platform, model) violated
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Model '{data.model_name}' already exists for platform '{data.platform_name}'"
        )

@router.post("/add_platform_model/", response_model=PlatformModelOut, status_code=status.HTTP_201_CREATED)
async def add_platform_model(model: PlatformModelIn):
    obj = await _create_platform_model(model)
    return PlatformModelOut(
        id=obj.id,
        platform_name=obj.platform.platform_name,
        model_name=obj.model,
        support=obj.support,
        is_active=obj.is_active
    )
