from agno.agent import Agent
from agno.models.openai import OpenAIChat
from dotenv import load_dotenv
import os
import sys
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import asyncio  # Add this import
from agno.models.openrouter import OpenRouter
from asgiref.sync import sync_to_async
# Set the path to your .env file
env_path = r"D:\finsocial\Multi model adding for the trading\.env"
load_dotenv(dotenv_path=env_path)
sys.path.append("D:/finsocial/Multi model adding for the trading")
from components.translator import LanguageTranslator
from components.language_check import language_check


router = APIRouter()


# Create an enhancement agent
enhancement_agent = Agent(
    model=OpenRouter(id=os.getenv("enchance_model"), api_key=os.getenv("enchance_model_api_key")),
    instructions="""You are a prompt enhancement specialist. Your job is to rewrite prompts to be more specific, explicit, and helpful for large language models.

    When given a prompt, you should:
    - Clarify vague phrases
    - Add specific details where needed
    - Make the intent clearer
    - Keep it concise but comprehensive
    - Return only the enhanced prompt without additional commentary""",
    markdown=False
)

# Your custom prompt-enhancing function (removed @tool decorator)
def enhance_prompt(prompt: str) -> str:
    """
    Enhances a basic prompt to make it more effective for LLMs.
    
    Args:
        prompt: The original prompt to enhance
        
    Returns:
        Enhanced version of the prompt
    """
    enhancement_request = f"""Please enhance this prompt:

Original prompt: {prompt}

Provide only the enhanced version:"""
    
    # Use the enhancement agent
    response = enhancement_agent.run(enhancement_request)
    return response.content.strip()



@router.get("/enhance-prompt/", response_model=dict)
async def enhance_prompt_endpoint(prompt: str, language_name: str, language_code: str) -> dict:
    if len(prompt) < 20:
        return {"enhanced_prompt_error": "Prompt is too short"}

    TRANSLATION_TIMEOUT = 20
    translator = LanguageTranslator()
    check_code = language_check(language_code)
    translating = None
    if check_code == False:   
        try:
            translating = await asyncio.wait_for(
                                translator.translate_text_async(
                                    text=prompt, 
                                    source_lang=language_code, 
                                    target_lang='eng_Latn'
                                ),
                                timeout=TRANSLATION_TIMEOUT
                            )
            result = enhance_prompt(translating)
            now_Trans = await asyncio.wait_for(
                                translator.translate_text_async(
                                    text=result, 
                                    source_lang='eng_Latn', 
                                    target_lang=language_code
                                ),
                                timeout=TRANSLATION_TIMEOUT
                            )
            
            return {"enhanced_prompt": now_Trans}
        except asyncio.TimeoutError:
            return {"enhanced_prompt_error": "Translation timed out"}
        except Exception as e:
            return {"enhanced_prompt_error": "Check your language code and name"}
    else:
        result = enhance_prompt(prompt)
        return {"enhanced_prompt": result}

