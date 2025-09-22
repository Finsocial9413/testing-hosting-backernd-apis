from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
import sys
import os

# Add the agents directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'agents'))

from suggested_agent import create_suggested_agent

# Create router
router = APIRouter(prefix="/suggestions", tags=["suggestions"])

# Request model
class SuggestionRequest(BaseModel):
    last_response: str
    user_input: str

# Response model
class SuggestionResponse(BaseModel):
    suggestions: List[str]
    status: str = "success"

@router.post("/generate", response_model=SuggestionResponse)
async def generate_suggestions_api(request: SuggestionRequest):
    """
    Generate follow-up prompt suggestions based on last response and user input
    
    Args:
        request: Contains last_response and user_input
        
    Returns:
        List of suggested follow-up prompts
    """
    try:
        if not request.last_response.strip() or not request.user_input.strip():
            raise HTTPException(
                status_code=400, 
                detail="Both last_response and user_input are required and cannot be empty"
            )
        
        # Generate suggestions using the suggested agent
        suggestions = create_suggested_agent(
            response=request.last_response,
            user_input=request.user_input
        )
        
        return SuggestionResponse(
            suggestions=suggestions,
            status="success"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating suggestions: {str(e)}"
        )
