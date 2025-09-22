from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from asgiref.sync import sync_to_async
from django.db import IntegrityError
from .models import AIModel
from decimal import Decimal

router = APIRouter()

# Pydantic schemas
class AIModelBase(BaseModel):
    model_name: str
    backend_model_name: str
    input_price_per_token: float
    output_price_per_token: float
    provider: Optional[str] = ""
    is_active: bool = True

class AIModelCreate(AIModelBase):
    pass

class AIModelResponse(AIModelBase):
    id: int
    created_at: str
    updated_at: str

    class Config:
        orm_mode = True

def _to_response(instance: AIModel) -> AIModelResponse:
    return AIModelResponse(
        id=instance.id,
        model_name=instance.model_name,
        backend_model_name=instance.backend_model_name,
        input_price_per_token=float(Decimal(instance.input_price_per_token)),
        output_price_per_token=float(Decimal(instance.output_price_per_token)),
        provider=instance.provider,
        is_active=instance.is_active,
        created_at=instance.created_at.isoformat(),
        updated_at=instance.updated_at.isoformat(),
    )


@router.get("/ai-models/", response_model=List[AIModelResponse])
async def list_ai_models(include_inactive: bool = True):
    qs = AIModel.objects.all() if include_inactive else AIModel.objects.filter(is_active=True)
    models = await sync_to_async(list)(qs)
    return [_to_response(m) for m in models]

