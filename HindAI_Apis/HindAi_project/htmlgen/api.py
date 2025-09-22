from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
from django.contrib.auth import get_user_model
from asgiref.sync import sync_to_async
from .models import HtmlGeneration
from .html_code_generation.html_gen import generate_html

router = APIRouter()

# Request model for HTML generation
class HtmlGenerationRequest(BaseModel):
    username: str
    prompt: str
    answer: str

# Response model for HTML generation
class HtmlGenerationResponse(BaseModel):
    id: int
    username: str
    prompt: str
    html: str
    message: str = "HTML generated successfully"

@router.post("/generate", response_model=HtmlGenerationResponse)
async def create_html(request: HtmlGenerationRequest):
    """
    Generate HTML based on a prompt and answer and save it to the database.
    If an entry with the given answer already exists for the user, return that instead.
    """
    try:
        # Get the User model
        UserModel = get_user_model()
        
        # Find the user by username
        @sync_to_async
        def get_user():
            try:
                return UserModel.objects.get(username=request.username)
            except UserModel.DoesNotExist:
                return None
        
        user = await get_user()
        if not user:
            raise HTTPException(status_code=404, detail=f"User {request.username} not found")
        
        # Check if an HTML generation record with the same answer already exists
        @sync_to_async
        def get_existing_record():
            return HtmlGeneration.objects.filter(answer=request.answer).first()
        
        existing_record = await get_existing_record()
        if existing_record:
            return {
                "id": existing_record.id,
                "username": user.username,
                "prompt": existing_record.prompt,
                "html": existing_record.html,
                "message": "HTML retrieved successfully"
            }
        
        # Generate HTML from the answer using the prompt for context
        full_prompt = f"{request.answer}"
        html_content = generate_html(full_prompt)
        
        # Save the HTML generation to the database
        @sync_to_async
        def create_html_record():
            html_gen = HtmlGeneration.objects.create(
                user=user,
                answer=request.answer,
                prompt=request.prompt,
                html=html_content
            )
            return html_gen
        
        html_generation = await create_html_record()
        
        return {
            "id": html_generation.id,
            "username": user.username,
            "prompt": html_generation.prompt,
            "html": html_generation.html,
            "message": "HTML generated successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating HTML: {str(e)}")