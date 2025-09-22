from fastapi import APIRouter, HTTPException, BackgroundTasks, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from typing import Optional

import asyncio
import uuid
from asyncio import create_task
import sys
import os

# Import the new task manager
from .task_manager import task_manager
# Add this import with your other imports
from dotenv import load_dotenv
sys.path.append("D:/finsocial/Multi model adding for the trading")
from se import run_agent
from token_Generation.token_gen import count_tokens
from components.generate_unique_chat_id import generate_unique_id, sanitize_chat_id
from components.language_check import language_check
from components.google_search_tools import get_google_Search_tools
from components.translator import LanguageTranslator
from agents.reasioning_agent import get_detailed_reasoning
# from agents.minimizing_reasioning_agent import show_reasoning_finals
from .userchat_data import get_userchats, read_json_file,get_chat_content,get_chat_content_for_token
sys.path.append("D:/finsocial/Multi model adding for the trading/HindAI_Apis/HindAi_project")
from gpt_models.models import AIModel
from user_credits.api import add_credits,deduct_credits,DeductCreditsRequest
from small_codes.check_user_exist import get_user_connections
from model_selection.model_Selection import choose_models
from asgiref.sync import sync_to_async
# Load environment variables from .env file
load_dotenv()
base_path_for_chat = os.getenv("BASE_PATH_FOR_CHAT")

# Configuration for timeouts
REASONING_TIMEOUT = 60  # Increased from 30 to 60 seconds
TRANSLATION_TIMEOUT = 20  # Increased from 15 to 20 seconds
AGENT_TIMEOUT = 150  # Increased from 120 to 150 seconds
MCP_TIMEOUT = 15  # Increased from 10 to 15 seconds


router = APIRouter()

# Define a request model for the input parameters
class RunAgentRequest(BaseModel):
    username: str = 'user'
    chat_id: str ='new'
    api: str = 'no'
    api_reasoning_platform: str = 'no'
    api_final_model_platform: str = 'no'
    model_name: str = 'google/gemini-2.5-pro'
    reasoning_model_name: str = 'google/gemini-2.5-pro'
    reasoning : bool = False
    message: str ='hello what is your name?'
    language: str = 'English'
    language_code: str = 'eng_Latn'
    google_search: str = 'n'
    deep_google_search: str = 'n'
    current_time: str = '2025-08-01T00:00:00Z'
    

# Add the TaskResponse model
class TaskResponse(BaseModel):
    task_id: str
    status: str
    chat_id: Optional[str] = None
    error: Optional[str] = None

@sync_to_async
def get_token_prices(backend_model_name):
    try:
        model = AIModel.objects.get(backend_model_name=backend_model_name)
        return {
            "input_price_per_token": float(model.input_price_per_token),
            "output_price_per_token": float(model.output_price_per_token),
        }
    except AIModel.DoesNotExist:
        return None


@router.post("/run-agent")
async def run_agent_endpoint(request: RunAgentRequest, background_tasks: BackgroundTasks):
    """
    Endpoint to start the agent process in the background and return a task ID.
    
    Args:
        request: JSON payload containing all required parameters.
        
    Returns:
        A task ID that can be used to stream or cancel the response.
    """
    try:
        # Generate task ID
        task_id = str(uuid.uuid4())

        # Initialize task status using task manager
        initial_task_data = {
            "status": "processing",
            "reasoning_stream": [],
            "final_response": None,
            "cancelled": False
        }
        task_manager.save_task(task_id, initial_task_data)
        
        # Start processing in background
        background_tasks.add_task(
            process_agent_request, 
            request=request, 
            task_id=task_id
        )
        
        # Return task ID immediately
        return TaskResponse(task_id=task_id, status="processing")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error occurred: {str(e)}")

async def process_agent_request(request: RunAgentRequest, task_id: str):
    """Background task to process the agent request."""
    
    if request.api == 'yes':
        print("yes")
        try:

            # check if username is available or not
            if await get_user_connections(request.username) == False:
                task_manager.update_task(task_id, {
                    "username": request.username,
                    "status": "completed",
                    "reasoning_stream": ["current user is not available"],
                    "final_response": "current user is not available"
                })
                return
             
            translator = LanguageTranslator()
            check_code = language_check(request.language_code)
            if check_code == False:
                request_message = await asyncio.wait_for(
                        translator.translate_text_async(
                            text=request.message, 
                            source_lang=request.language_code,
                            target_lang='eng_Latn'
                        ),
                        timeout=TRANSLATION_TIMEOUT
                    )
                print("change the prompt to english")
            else:
                print("prompt is already in english")
                request_message = request.message
                
            
            # Generate chat ID if needed
            if request.chat_id == 'new':
                chat_id = generate_unique_id()
                chat_id = sanitize_chat_id(chat_id)
                
            else:
                get_The_chat_Conetent = get_chat_content_for_token(request.username, request.chat_id)
                chat_id = request.chat_id

            # Store chat_id in task
            task_manager.update_task(task_id, {"chat_id": chat_id})
            # Get reasoning with timeout and retry logic
            max_reasoning_retries = 2
            get_reasonings = None
            get_enable_disable = request.reasoning


            # getting the reasoning models

            selected_models = await choose_models(
                username = request.username,
                reasoning_model_platform=request.api_reasoning_platform,
                final_model_platform=request.api_final_model_platform,
                reasoning_model_name=request.reasoning_model_name,
                final_model_name=request.model_name,
                reasoning=request.reasoning
            )




            for reasoning_attempt in range(max_reasoning_retries + 1):
                try:
                    print(f"Starting reasoning attempt {reasoning_attempt + 1}/{max_reasoning_retries + 1} for task {task_id}")
                    # reasoning_model, question, chat_id , username,current_time,base_path
                    if get_enable_disable ==  True:
                        get_reasonings = await asyncio.wait_for(
                            get_detailed_reasoning(
                                reasoning_model = request.reasoning_model_name,
                                question =request_message, 
                                chat_id=str(chat_id),
                                username=request.username,
                                current_time=request.current_time,
                                base_path=base_path_for_chat,
                                api = request.api,
                                model_config = selected_models["reasoning_model"]
                            ),
                            timeout=REASONING_TIMEOUT
                        )
   
                        print(f"Reasoning generation successful for task {task_id}")
                    
                        break  # Success, exit retry loop
                    else:
                        get_reasonings = 'No reasoning for this request'
                        break  # No reasoning needed, exit loop
                    
                except asyncio.TimeoutError:
                    print(f"Reasoning timeout on attempt {reasoning_attempt + 1} for task {task_id}")
                    if reasoning_attempt < max_reasoning_retries:
                        print(f"Retrying reasoning in 3 seconds...")
                        await asyncio.sleep(3)
                        continue
                    else:
                        # Final fallback - use a simple reasoning
                        print(f"Using fallback reasoning for task {task_id}")
                        
                        get_reasonings = f"Analyzing the user's question: '{request.message}'. This appears to be a request that requires careful consideration of the context and appropriate response generation."
                        break
                        
                except Exception as e:
                    print(f"Error in get_detailed_reasoning: {str(e)}")
                    error_msg = str(e).lower()
                    if 'No auth credentials found' in error_msg:
                        print("I am herre in respomse")
                        task_manager.update_task(task_id, {
                            "username": request.username,
                            "status": "completed",
                            "final_response": "Provided API is not correct check your api again",
                            "reasoning_stream": [
                                "Insufficient credits to complete the final answer generation. Please add credits and try again."
                            ]
                        })
                        return
                    print(f"Reasoning generation error on attempt {reasoning_attempt + 1}: {str(e)}")
                    if reasoning_attempt < max_reasoning_retries:
                        await asyncio.sleep(2)
                        continue
                    else:
                        # Use fallback reasoning
                        get_reasonings = f"Processing user request: '{request.message}'. Generating appropriate response based on available context."
                        break
            
            if get_reasonings == "Provided API is not correct check your api again_secretkey_to_remove_anyother_type_of_the_confusion123454645451215451545":
                task_manager.update_task(task_id, {
                    "username": request.username,
                    "status": "completed",
                    "reasoning_stream": ["Provided API is not correct check your api again"],
                    "final_response": "Provided API is not correct check your api again."
                })
                return

            # Check if task was cancelled
            current_task = task_manager.get_task(task_id)
            if current_task and current_task.get("cancelled", False):
                task_manager.update_task(task_id, {
                    "username": request.username,
                    "status": "cancelled"
                })
                return
            # Check if task was cancelled
            if current_task and current_task.get("cancelled", False):
                task_manager.update_task(task_id, {
                    "username": request.username,
                    "status": "cancelled"
                })
                return
                
            check_code = language_check(request.language_code)
            show_res = get_reasonings
            if check_code == False:
                try:
                    get_trans_reasonings = await asyncio.wait_for(
                        translator.translate_text_async(
                            text=get_reasonings, 
                            source_lang='eng_Latn', 
                            target_lang=request.language_code
                        ),
                        timeout=TRANSLATION_TIMEOUT
                    )
                    # Store the translated reasoning
                    task_manager.update_task(task_id, {"translated_reasoning": get_trans_reasonings})
                except asyncio.TimeoutError:
                    print(f"Translation timed out for task {task_id}, using original text")
                    get_trans_reasonings = show_res  # Fallback to original
                    task_manager.update_task(task_id, {"translated_reasoning": show_res})
                except Exception as e:
                    print(f"Error in translation: {e}")
                    get_trans_reasonings = show_res  # Fallback to original
                    task_manager.update_task(task_id, {"translated_reasoning": show_res})
            else:
                get_trans_reasonings = ''
                task_manager.update_task(task_id, {"translated_reasoning": None})
                
            if check_code == False:
                # Store reasoning in the task status (for streaming)
                current_task = task_manager.get_task(task_id)
                reasoning_stream = current_task.get("reasoning_stream", [])
                reasoning_stream.append(get_trans_reasonings)
                task_manager.update_task(task_id, {"reasoning_stream": reasoning_stream})
            else: 
                current_task = task_manager.get_task(task_id)
                reasoning_stream = current_task.get("reasoning_stream", [])
                reasoning_stream.append(show_res)
                task_manager.update_task(task_id, {"reasoning_stream": reasoning_stream})

            # Check if task was cancelled again    
            current_task = task_manager.get_task(task_id)
            if current_task and current_task.get("cancelled", False):
                task_manager.update_task(task_id, {
                    "username": request.username,
                    "status": "cancelled"
                })
                return
                
            # Generate final response with enhanced timeout and retry handling
            max_retries = 3  # Increased retries
            retry_delay = 3  # Increased delay
            
            for attempt in range(max_retries + 1):
                try:
                    print(f"Starting agent call attempt {attempt + 1}/{max_retries + 1} for task {task_id}")
                    
                    # Create a wrapper function that handles MCP timeouts specifically
                    async def run_agent_with_mcp_handling():
                        try:
                            returning_the_final_answer = await run_agent(
                                model_name = request.model_name,
                                message=request.message,
                                username=request.username,
                                chat_id=str(chat_id),
                                language=request.language,
                                language_code=request.language_code,
                                translator=translator,
                                google_search=request.google_search,
                                deep_google_search=request.deep_google_search,
                                current_time=request.current_time,
                                get_reasonings=get_reasonings,
                                get_trans_reasonings=get_trans_reasonings,
                                get_reasoning_status=get_enable_disable,
                                api = request.api,
                                model_config=selected_models['final_model']
                            )
                            if returning_the_final_answer =="Provided API is not correct check your api again_secretkey_to_remove_anyother_type_of_the_confusion12345464545121545154":
                                task_manager.update_task(task_id, {
                                    "status": "completed",
                                    "final_response": "Provided API is not correct check your api again"
                                })
                                
                                return
                            return returning_the_final_answer
                        except Exception as e:
                            print("i am here in error handling part bro")
                            error_msg = str(e).lower()
                            if 'API status error'.lower() in error_msg:
                                task_manager.update_task(task_id, {
                                    "status": "completed",
                                    "final_response": "Provided API is not correct check your api again"
                                })
                                return
                                
                            print(f"Agent execution error: {str(e)}")
                            # Handle MCP-specific errors
                            if any(mcp_keyword in error_msg for mcp_keyword in [
                                "failed to get mcp tools",
                                "mcp",
                                "clientrequest",
                                "timed out while waiting for response",
                                "connection error",
                                "timeout"
                            ]):
                                print(f"MCP/Timeout error detected: {str(e)}")
                                # For MCP errors, we'll return a fallback response
                                return "I apologize, but I'm experiencing some technical difficulties with external tools. Please try your request again in a moment."
                            raise  # Re-raise non-MCP errors
                    
                    result = await asyncio.wait_for(
                        run_agent_with_mcp_handling(),
                        timeout=AGENT_TIMEOUT
                    )
                    
                    print(f"Agent call successful for task {task_id}")
                    break  # Success, exit retry loop
                    
                except asyncio.TimeoutError:
                    error_message = f"Request timed out after {AGENT_TIMEOUT} seconds on attempt {attempt + 1}"
                    print(f"AsyncIO timeout on attempt {attempt + 1} for task {task_id}")
                    if attempt < max_retries:
                        print(f"Retrying in {retry_delay} seconds...")
                        await asyncio.sleep(retry_delay)
                        continue
                    else:
                        task_manager.update_task(task_id, {
                            "status": "error",
                            "error": "The AI service is experiencing delays. Please try again in a few moments."
                        })
                        print(f"Task {task_id}: Final timeout after all retries")
                        return
                        
                except Exception as e:
                    error_msg = str(e).lower()
                    print(f"Exception on attempt {attempt + 1} for task {task_id}: {str(e)}")
                    
                    # Check for timeout-related errors (including MCP timeouts)
                    if any(keyword in error_msg for keyword in [
                        "timed out while waiting for response", 
                        "timeout", 
                        "clientrequest", 
                        "connection timeout",
                        "read timeout",
                        "request timeout",
                        "failed to get mcp tools",
                        "connection error"
                    ]):
                        if attempt < max_retries:
                            print(f"Timeout/MCP error, retrying in {retry_delay} seconds...")
                            await asyncio.sleep(retry_delay)
                            continue
                        else:
                            task_manager.update_task(task_id, {
                                "status": "error",
                                "error": f"Service connectivity issues: {str(e)[:100]}..."
                            })
                            print(f"Task {task_id}: Final connectivity error after all retries")
                            return
                    else:
                        # Non-timeout error, don't retry
                        task_manager.update_task(task_id, {
                            "status": "error",
                            "error": f"Processing error: {str(e)[:100]}..."
                        })
                        print(f"Task {task_id}: Non-timeout error - {str(e)}")
                        return
            
            # Final check for cancellation
            current_task = task_manager.get_task(task_id)
            if current_task and current_task.get("cancelled", False):
                task_manager.update_task(task_id, {
                    "status": "cancelled"
                })
                return
                
            # Store final results
            task_manager.update_task(task_id, {
                "final_response": result['response'],
                "username": request.username,
                "status": "completed"
            })
            
            print(f"Task {task_id} completed successfully")

        except Exception as e:
            # Handle any exceptions and update task status
            print(f"Unexpected error in processing task {task_id}: {e}")
            error_msg = str(e).lower()
            if any(keyword in error_msg for keyword in [
                "timeout", "timed out", "clientrequest", "mcp", "failed to get mcp tools", "connection"
            ]):
                error_detail = f"Service temporarily unavailable: {str(e)[:100]}..."
            else:
                error_detail = f"Unexpected error occurred: {str(e)[:100]}..."
            
            task_manager.update_task(task_id, {
                "status": "error",
                "error": error_detail
            })

    else:
        try:
            print("i am not here")
            print("API details ")
            # check if username is available or not
            if await get_user_connections(request.username) == False:
                task_manager.update_task(task_id, {
                    "status": "completed",
                    "reasoning_stream": ["current user is not available"],
                    "final_response": "current user is not available"
                })
                return
                
            get_enable_disable = request.reasoning
            get_res_mode = request.reasoning_model_name
            get_final_answer_model = request.model_name
            get_res_mode_credit = await get_token_prices(get_res_mode)
            get_final_answer_model_credit = await get_token_prices(get_final_answer_model)
            # per_token_pricing calculating 
            per_token_res_input_price = get_res_mode_credit['input_price_per_token'] / 10
            per_token_final_answer_input_price = get_final_answer_model_credit['input_price_per_token'] / 10       
            per_token_res_output_price = get_res_mode_credit['output_price_per_token'] / 10
            per_token_final_answer_output_price = get_final_answer_model_credit['output_price_per_token'] / 10
            # Initialize the translator
            # we have translated the user prompt to english if the language code is not english
            translator = LanguageTranslator()
            check_code = language_check(request.language_code)
            if check_code == False:
                request_message = await asyncio.wait_for(
                        translator.translate_text_async(
                            text=request.message, 
                            source_lang=request.language_code,
                            target_lang='eng_Latn'
                        ),
                        timeout=TRANSLATION_TIMEOUT
                    )
                print("change the prompt to english")
            else:
                print("prompt is already in english")
                request_message = request.message
                
            
            # Generate chat ID if needed
            if request.chat_id == 'new':
                total_token_from_previous_chat =0
                chat_id = generate_unique_id()
                chat_id = sanitize_chat_id(chat_id)
                
            else:
                get_The_chat_Conetent = get_chat_content_for_token(request.username, request.chat_id)
                total_token_from_previous_chat = count_tokens(str(get_The_chat_Conetent))
                chat_id = request.chat_id

            # Store chat_id in task
            task_manager.update_task(task_id, {"chat_id": chat_id})
            

            # saving the tokens informations for the both reasoning input and output tokens 
            get_input_token_counts = count_tokens(request.message) + total_token_from_previous_chat
            get_res_mode_input_token_price = get_input_token_counts * per_token_res_input_price  
            try: 
                deduct_request = DeductCreditsRequest(
                    username=request.username,
                    amount=get_res_mode_input_token_price  # your calculated amount
                    )
                credit_result = await deduct_credits(deduct_request)
                print(f"Deducted credits for reasoning input: {credit_result}")
            except Exception as e:
                err = str(e)
                if "insufficient credits" in err.lower():
                    task_manager.update_task(task_id, {
                        "username": request.username,
                        "status": "completed",
                        "reasoning_stream": [
                            "Insufficient credits to complete the reasoning generation. Please add credits and try again."
                        ],
                        "final_response": "Insufficient credits to complete the final answer generation. Please add credits and try again."
                    })
                    return
            
            
            # Get reasoning with timeout and retry logic
            max_reasoning_retries = 2
            get_reasonings = None
            
            for reasoning_attempt in range(max_reasoning_retries + 1):
                try:
                    print(f"Starting reasoning attempt {reasoning_attempt + 1}/{max_reasoning_retries + 1} for task {task_id}")
                    # reasoning_model, question, chat_id , username,current_time,base_path
                    if get_enable_disable ==  True:
                        get_reasonings = await asyncio.wait_for(
                            get_detailed_reasoning(
                                reasoning_model = request.reasoning_model_name,
                                question =request_message, 
                                chat_id=str(chat_id),
                                username=request.username,
                                current_time=request.current_time,
                                base_path=base_path_for_chat,
                                api=request.api,
                                model_config=''
                            ),
                            timeout=REASONING_TIMEOUT
                        )
                        print(f"Reasoning generation successful for task {task_id}")
                    
                        break  # Success, exit retry loop
                    else:
                        get_reasonings = 'No reasoning for this request'
                        break  # No reasoning needed, exit loop
                    
                except asyncio.TimeoutError:
                    print(f"Reasoning timeout on attempt {reasoning_attempt + 1} for task {task_id}")
                    if reasoning_attempt < max_reasoning_retries:
                        print(f"Retrying reasoning in 3 seconds...")
                        await asyncio.sleep(3)
                        continue
                    else:
                        # Final fallback - use a simple reasoning
                        print(f"Using fallback reasoning for task {task_id}")
                        
                        get_reasonings = f"Analyzing the user's question: '{request.message}'. This appears to be a request that requires careful consideration of the context and appropriate response generation."
                        break
                        
                except Exception as e:
                    print(f"Error in get_detailed_reasoning: {str(e)}")
                    error_msg = str(e).lower()
                    if 'No auth credentials found' in error_msg:
                        task_manager.update_task(task_id, {
                            "username": request.username,
                            "status": "completed",
                            "final_response": "Provided API is not correct check your api again",
                            "reasoning_stream": [
                                "Insufficient credits to complete the final answer generation. Please add credits and try again."
                            ]
                        })
                        return
                    print(f"Reasoning generation error on attempt {reasoning_attempt + 1}: {str(e)}")
                    if reasoning_attempt < max_reasoning_retries:
                        await asyncio.sleep(2)
                        continue
                    else:
                        # Use fallback reasoning
                        get_reasonings = f"Processing user request: '{request.message}'. Generating appropriate response based on available context."
                        break
            


            if get_reasonings == "Provided API is not correct check your api again_secretkey_to_remove_anyother_type_of_the_confusion123454645451215451545":
                task_manager.update_task(task_id, {
                    "username": request.username,
                    "status": "completed",
                    "reasoning_stream": ["Provided API is not correct check your api again"],
                    "final_response": "Provided API is not correct check your api again."
                })
                return
                
                
            # this is for the reasoning model output token price
            get_input_token_counts = count_tokens(get_reasonings)
            get_res_mode_output_token_price = get_input_token_counts * per_token_res_output_price  
            
            try:
                deduct_request = DeductCreditsRequest(
                username=request.username,
                amount=get_res_mode_output_token_price  # your calculated amount
                )
                credit_result = await deduct_credits(deduct_request)
                print(f"Deducted credits for reasoning output: {credit_result}")
            except Exception as e:
                err = str(e)
                if "insufficient credits" in err.lower():
                    task_manager.update_task(task_id, {
                        "username": request.username,
                        "status": "completed",
                        "reasoning_stream": [
                            "Insufficient credits to complete the final answer generation. Please add credits and try again."
                        ],
                        "final_response": "Insufficient credits to complete the final answer generation. Please add credits and try again."
                    })
                    return
            
            
            # this is for the input final answer model 
            res_in_input_for_final_answer = count_tokens(get_reasonings)
            get_input_message_token = count_tokens(request.message)
            get_input_token_for_final_answer_counts = res_in_input_for_final_answer + get_input_message_token + total_token_from_previous_chat
            get_final_answer_model_input_token_price = get_input_token_for_final_answer_counts * per_token_final_answer_input_price
            
            try:
                deduct_request = DeductCreditsRequest(
                        username=request.username,
                        amount=get_final_answer_model_input_token_price  # your calculated amount
                    )
                credit_result = await deduct_credits(deduct_request)
                print(f"Deducted credits for final answer Input_Tokens model input: {credit_result}")
            except Exception as e:
                err = str(e)
                if "insufficient credits" in err.lower():
                    task_manager.update_task(task_id, {
                        "username": request.username,
                        "status": "completed",
                        "final_response": "Insufficient credits to complete the final answer generation. Please add credits and try again."
                    })
                    return


            # Check if task was cancelled
            current_task = task_manager.get_task(task_id)
            if current_task and current_task.get("cancelled", False):
                task_manager.update_task(task_id, {
                    "status": "cancelled"
                })
                return
                

            
            # Check if task was cancelled
            if current_task and current_task.get("cancelled", False):
                task_manager.update_task(task_id, {
                    "status": "cancelled"
                })
                return
                
            check_code = language_check(request.language_code)
            show_res = get_reasonings
            if check_code == False:
                try:
                    get_trans_reasonings = await asyncio.wait_for(
                        translator.translate_text_async(
                            text=get_reasonings, 
                            source_lang='eng_Latn', 
                            target_lang=request.language_code
                        ),
                        timeout=TRANSLATION_TIMEOUT
                    )
                    # Store the translated reasoning
                    task_manager.update_task(task_id, {"translated_reasoning": get_trans_reasonings})
                except asyncio.TimeoutError:
                    print(f"Translation timed out for task {task_id}, using original text")
                    get_trans_reasonings = show_res  # Fallback to original
                    task_manager.update_task(task_id, {"translated_reasoning": show_res})
                except Exception as e:
                    print(f"Error in translation: {e}")
                    get_trans_reasonings = show_res  # Fallback to original
                    task_manager.update_task(task_id, {"translated_reasoning": show_res})
            else:
                get_trans_reasonings = ''
                task_manager.update_task(task_id, {"translated_reasoning": None})
                
            if check_code == False:
                # Store reasoning in the task status (for streaming)
                current_task = task_manager.get_task(task_id)
                reasoning_stream = current_task.get("reasoning_stream", [])
                reasoning_stream.append(get_trans_reasonings)
                task_manager.update_task(task_id, {"reasoning_stream": reasoning_stream})
            else: 
                current_task = task_manager.get_task(task_id)
                reasoning_stream = current_task.get("reasoning_stream", [])
                reasoning_stream.append(show_res)
                task_manager.update_task(task_id, {"reasoning_stream": reasoning_stream})

            # Check if task was cancelled again    
            current_task = task_manager.get_task(task_id)
            if current_task and current_task.get("cancelled", False):
                task_manager.update_task(task_id, {
                    "username": request.username,
                    "status": "cancelled"
                })
                return
                
            # Generate final response with enhanced timeout and retry handling
            max_retries = 3  # Increased retries
            retry_delay = 3  # Increased delay
            
            for attempt in range(max_retries + 1):
                try:
                    print(f"Starting agent call attempt {attempt + 1}/{max_retries + 1} for task {task_id}")
                    
                    # Create a wrapper function that handles MCP timeouts specifically
                    async def run_agent_with_mcp_handling():
                        print("i am here in task id")
                        try:
                            returning_the_final_answer = await run_agent(
                                model_name = request.model_name,
                                message=request.message,
                                username=request.username,
                                chat_id=str(chat_id),
                                language=request.language,
                                language_code=request.language_code,
                                translator=translator,
                                google_search=request.google_search,
                                deep_google_search=request.deep_google_search,
                                current_time=request.current_time,
                                get_reasonings=get_reasonings,
                                get_trans_reasonings=get_trans_reasonings,
                                get_reasoning_status=get_enable_disable,
                                api=request.api,
                                model_config='',
                                task_id = task_id,
                            )
                            if returning_the_final_answer =="Provided API is not correct check your api again_secretkey_to_remove_anyother_type_of_the_confusion12345464545121545154":
                                task_manager.update_task(task_id, {
                                    "status": "completed",
                                    "final_response": "Provided API is not correct check your api again"
                                })
                                return
                            return returning_the_final_answer
                        except Exception as e:
                            print("i am here in error handling part bro")
                            error_msg = str(e).lower()
                            if 'API status error'.lower() in error_msg:
                                task_manager.update_task(task_id, {
                                    "status": "completed",
                                    "final_response": "Provided API is not correct check your api again"
                                })
                                return
                                
                            print(f"Agent execution error: {str(e)}")
                            # Handle MCP-specific errors
                            if any(mcp_keyword in error_msg for mcp_keyword in [
                                "failed to get mcp tools",
                                "mcp",
                                "clientrequest",
                                "timed out while waiting for response",
                                "connection error",
                                "timeout"
                            ]):
                                print(f"MCP/Timeout error detected: {str(e)}")
                                # For MCP errors, we'll return a fallback response
                                return "I apologize, but I'm experiencing some technical difficulties with external tools. Please try your request again in a moment."
                            raise  # Re-raise non-MCP errors
                    
                    result = await asyncio.wait_for(
                        run_agent_with_mcp_handling(),
                        timeout=AGENT_TIMEOUT
                    )
                    
                    print(f"Agent call successful for task {task_id}")
                    break  # Success, exit retry loop
                    
                except asyncio.TimeoutError:
                    error_message = f"Request timed out after {AGENT_TIMEOUT} seconds on attempt {attempt + 1}"
                    print(f"AsyncIO timeout on attempt {attempt + 1} for task {task_id}")
                    if attempt < max_retries:
                        print(f"Retrying in {retry_delay} seconds...")
                        await asyncio.sleep(retry_delay)
                        continue
                    else:
                        task_manager.update_task(task_id, {
                            "status": "error",
                            "error": "The AI service is experiencing delays. Please try again in a few moments."
                        })
                        print(f"Task {task_id}: Final timeout after all retries")
                        return
                        
                except Exception as e:
                    error_msg = str(e).lower()
                    print(f"Exception on attempt {attempt + 1} for task {task_id}: {str(e)}")
                    
                    # Check for timeout-related errors (including MCP timeouts)
                    if any(keyword in error_msg for keyword in [
                        "timed out while waiting for response", 
                        "timeout", 
                        "clientrequest", 
                        "connection timeout",
                        "read timeout",
                        "request timeout",
                        "failed to get mcp tools",
                        "connection error"
                    ]):
                        if attempt < max_retries:
                            print(f"Timeout/MCP error, retrying in {retry_delay} seconds...")
                            await asyncio.sleep(retry_delay)
                            continue
                        else:
                            task_manager.update_task(task_id, {
                                "status": "error",
                                "error": f"Service connectivity issues: {str(e)[:100]}..."
                            })
                            print(f"Task {task_id}: Final connectivity error after all retries")
                            return
                    else:
                        # Non-timeout error, don't retry
                        task_manager.update_task(task_id, {
                            "status": "error",
                            "error": f"Processing error: {str(e)[:100]}..."
                        })
                        print(f"Task {task_id}: Non-timeout error - {str(e)}")
                        return
            
            # Final check for cancellation
            current_task = task_manager.get_task(task_id)
            if current_task and current_task.get("cancelled", False):
                task_manager.update_task(task_id, {
                    "status": "cancelled"
                })
                return
                
            # Store final results
            task_manager.update_task(task_id, {
                "username": request.username,
                "final_response": result['response'],
                "status": "completed"
            })
            
            
            
            
            # deducting the final answer output price 
            count_final_answer_output_token = count_tokens(result['response'])
            
            get_final_answer_model_output_token_price = count_final_answer_output_token * per_token_final_answer_output_price

            try:
                deduct_request = DeductCreditsRequest(
                    username=request.username,
                    amount=get_final_answer_model_output_token_price  # your calculated amount
                )
                credit_result = await deduct_credits(deduct_request)
            
                print(f"Deducted credits for final answer Output_Tokens model input: {credit_result}")
            except Exception as e:
                err = str(e)
                if "insufficient credits" in err.lower():
                    task_manager.update_task(task_id, {
                        "status": "completed",
                        "username": request.username,
                        "final_response": "Insufficient credits to complete the final answer generation. Please add credits and try again."
                    })
                    return
                # Optional: you could refund previously deducted partial credits here if business logic requires.
            

            task_manager.update_task(task_id, {
                "username": request.username,
                "status": "completed"
            })
            
            print(f"Task {task_id} completed successfully")

        except Exception as e:
            # Handle any exceptions and update task status
            print(f"Unexpected error in processing task {task_id}: {e}")
            task_manager.update_task(task_id, {
                "status": "error",
                "error": f"Unexpected error occurred: {str(e)[:100]}..."
            })

@router.get("/task/{task_id}/status")
async def get_task_status(task_id: str):
    """Check the status of a task."""
    task = task_manager.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    response = {
        "task_id": task_id,
        "status": task["status"]
    }
    
    # Include error details if the task has failed
    if task["status"] == "error" and "error" in task:
        response["error"] = task["error"]
        
    # Include chat_id if available
    if "chat_id" in task:
        response["chat_id"] = task["chat_id"]
    
    return response
    
    
@router.get("/task/{task_id}/result")
async def get_task_result(task_id: str):
    """Get the final result of a task."""
    task = task_manager.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Check the task status and return appropriate response
    if not task["reasoning_stream"]:
        # Reasoning not yet available
        return {
            "status": "waiting_for_reasoning",
            "chat_id": task.get("chat_id"),
            "Reasoning": None,
            "AI Message": None,
            'Reasoning File': None,
            "Main content file": None
        }
    elif task["status"] == "processing":
        # Reasoning is available, but final answer is still being prepared
        translated_reasoning = task.get("translated_reasoning", None)
        return {
            "status": "final_answer_preparing",
            "chat_id": task.get("chat_id"),
            "Reasoning": translated_reasoning if translated_reasoning else task["reasoning_stream"][-1],
            "AI Message": None,
            'Reasoning File': None,
            "Main content file": None
        }
    elif task["status"] == "completed":
        get_username = task["username"]
        # Both reasoning and final answer are ready
        translated_reasoning = task.get("translated_reasoning", None)
        # creating a markdown file first here for the reasoning
        SAVE_DIR = f"D:/finsocial/Multi model adding for the trading/userChats/{get_username}/markdown/reasoning/{task.get("chat_id")}/"
        os.makedirs(SAVE_DIR, exist_ok=True)
        file_id = f"{task_id}.md"
        file_path_reasoning = os.path.join(SAVE_DIR, file_id)
        with open(file_path_reasoning, "w", encoding="utf-8") as f:
            f.write(translated_reasoning if translated_reasoning else task["reasoning_stream"][-1])
        # creating a markdown file first here for the main answer
        SAVE_DIR = f"D:/finsocial/Multi model adding for the trading/userChats/{get_username}/markdown/final_answer/{task.get("chat_id")}/"
        os.makedirs(SAVE_DIR, exist_ok=True)
        file_id = f"{task_id}.md"
        file_path_main_content = os.path.join(SAVE_DIR, file_id)
        with open(file_path_main_content, "w", encoding="utf-8") as f:
            f.write(task["final_response"])
        # Return the final result
        return {
            "status": "completed",
            "chat_id": task.get("chat_id"),
            "Reasoning": translated_reasoning if translated_reasoning else task["reasoning_stream"][-1],
            "AI Message": task["final_response"],
            'Reasoning File': f"{file_path_reasoning}",
            "Main content file": f"{file_path_main_content}"
        }
    elif task["status"] == "error":
        # Handle error case
        raise HTTPException(status_code=500, detail=task.get("error", "Unknown error"))
    elif task["status"] == "cancelled":
        # Handle cancelled case
        raise HTTPException(status_code=400, detail="Task was cancelled")

@router.post("/task/{task_id}/cancel")
async def cancel_task(task_id: str):
    """Cancel a running task."""
    task = task_manager.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    if task["status"] == "processing":
        task_manager.update_task(task_id, {"cancelled": True})
        return {"status": "cancellation_requested"}
    
    return {"status": task["status"]}

# For streaming, you'll need to use WebSocket

@router.websocket("/task/{task_id}/stream")
async def stream_task(websocket: WebSocket, task_id: str):
    """Stream the reasoning and results as they become available."""
    await websocket.accept()
    
    # Check if task exists
    task = task_manager.get_task(task_id)
    if not task:
        await websocket.send_json({"error": "Task not found"})
        await websocket.close()
        return
    
    print(f"WebSocket connected for task: {task_id}")
    print(f"Task status: {task['status']}")
    
    try:
        last_index = 0
        
        # Keep checking for updates until the task is done
        while True:
            # Check if task still exists
            task = task_manager.get_task(task_id)
            if not task:
                await websocket.send_json({"error": "Task no longer exists"})
                break
                
            current_status = task["status"]
            
            # Send any new reasoning chunks
            stream = task["reasoning_stream"]
            if last_index < len(stream):
                for i in range(last_index, len(stream)):
                    await websocket.send_json({
                        "type": "reasoning",
                        "content": stream[i]
                    })
                last_index = len(stream)
            
            # Check if task is completed, cancelled, or has error
            if current_status in ["completed", "cancelled", "error"]:
                # Send final result
                final_data = {
                    "type": "final",
                    "status": current_status
                }
                
                if current_status == "completed":
                    # adding the md files in the web socket
                    get_username = task["username"]
                    # Both reasoning and final answer are ready
                    translated_reasoning = task.get("translated_reasoning", None)
                    # creating a markdown file first here for the reasoning
                    SAVE_DIR = f"D:/finsocial/Multi model adding for the trading/userChats/{get_username}/markdown/reasoning/{task.get("chat_id")}/"
                    os.makedirs(SAVE_DIR, exist_ok=True)
                    file_id = f"{task_id}.md"
                    file_path_reasoning = os.path.join(SAVE_DIR, file_id)
                    with open(file_path_reasoning, "w", encoding="utf-8") as f:
                        f.write(translated_reasoning if translated_reasoning else task["reasoning_stream"][-1])
                    # creating a markdown file first here for the main answer
                    SAVE_DIR = f"D:/finsocial/Multi model adding for the trading/userChats/{get_username}/markdown/final_answer/{task.get("chat_id")}/"
                    os.makedirs(SAVE_DIR, exist_ok=True)
                    file_id = f"{task_id}.md"
                    file_path_main_content = os.path.join(SAVE_DIR, file_id)
                    with open(file_path_main_content, "w", encoding="utf-8") as f:
                        f.write(task["final_response"])
                    # Return the final result

                    final_data.update({
                        "reasoning": translated_reasoning if translated_reasoning else (task["reasoning_stream"][-1] if task["reasoning_stream"] else None),
                        "response": task.get("final_response"),
                        "chat_id": task.get("chat_id"),
                        'Reasoning File': f"{file_path_reasoning}",
                        "Main content file": f"{file_path_main_content}"
                    })
                elif current_status == "error":
                    final_data["error"] = task.get("error", "Unknown error")
                elif current_status == "cancelled":
                    final_data["message"] = "Task was cancelled"
                
                await websocket.send_json(final_data)
                break
            
            # Wait before next check
            await asyncio.sleep(0.5)
            
    except WebSocketDisconnect:
        print(f"WebSocket disconnected for task: {task_id}")
    except Exception as e:
        print(f"WebSocket error for task {task_id}: {e}")
        try:
            await websocket.send_json({"error": f"WebSocket error: {str(e)}"})
        except:
            pass
    finally:
        try:
            await websocket.close()
        except:
            pass

