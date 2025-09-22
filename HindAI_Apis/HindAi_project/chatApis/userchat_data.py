import shutil  # Add this import at the top of the file
from fastapi import FastAPI, HTTPException
from typing import List, Dict, Any
import os
import sys
import importlib.util
from dotenv import load_dotenv
from agno.api.routes import ApiRoutes
# Import userchats module dynamically
spec = importlib.util.spec_from_file_location(
    "userchats", 
    "D:/finsocial/Multi model adding for the trading/FastApi_component/userchats.py"
)
userchats = importlib.util.module_from_spec(spec)
spec.loader.exec_module(userchats)
get_userchats = userchats.get_userchats
read_json_file = userchats.read_json_file
from fastapi import APIRouter
load_dotenv()
base_path_for_chat = os.getenv("BASE_PATH_FOR_CHAT")

router = APIRouter()

@router.get("/chats/{username}", response_model=List[Dict[str, str]])
async def get_user_chats(username: str):
    """
    Get all chats for a specific user.
    
    Args:
        username: The username to get chats for
        
    Returns:
        List of chat information including message and chat_id
    """
    directory = f"{base_path_for_chat}/{username}/Json"
    
    # Check if directory exists
    if not os.path.exists(directory):
        raise HTTPException(status_code=404, detail=f"User {username} not found")
        
    chats = get_userchats(directory)
    return chats

@router.get("/chats/{username}/{chat_id}", response_model=List[Dict[str, Any]])
async def get_chat_content(username: str, chat_id: str):
    """
    Get the content of a specific chat.
    
    Args:
        username: The username of the chat owner
        chat_id: The ID of the chat to retrieve
        
    Returns:
        The chat content as a list of messages
    """
    file_path = f"{base_path_for_chat}/{username}/Json/{chat_id}.json"
    
    # Check if file exists
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail=f"Chat {chat_id} not found")
        
    chat_content = read_json_file(file_path)
    if chat_content is None:
        raise HTTPException(status_code=500, detail=f"Error reading chat {chat_id}")
        
    return chat_content


@router.delete("/chats/delete/{username}")
async def delete_all_user_chats(username: str):
    """
    Delete all chats for a specific user.
    
    Args:
        username: The username whose chats should be deleted
        
    Returns:
        Confirmation message of deletion
    """
    directory1 = f"{base_path_for_chat}/{username}/Json"
    
    # Check if directory exists
    if not os.path.exists(directory1):
        raise HTTPException(status_code=404, detail=f"User {username} not found")
    
    try:
        # Delete all JSON files in the directory
        for filename in os.listdir(directory1):
            if filename.endswith('.json'):
                os.remove(os.path.join(directory1, filename))

        # Delete all files in the SqlDB directory
        
        return {"message": f"All chats for user {username} have been deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting chats: {str(e)}")

@router.delete("/chats/delete/{username}/{chat_id}")
async def delete_specific_chat(username: str, chat_id: str):
    """
    Delete a specific chat for a user.
    
    Args:
        username: The username of the chat owner
        chat_id: The ID of the chat to delete
        
    Returns:
        Confirmation message of deletion
    """
    file_path = f"{base_path_for_chat}/{username}/Json/{chat_id}.json"
    
    # Check if file exists
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail=f"Chat {chat_id} not found")
    
    try:
        os.remove(file_path)
        return {"message": f"Chat {chat_id} for user {username} has been deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting chat: {str(e)}")
    
    
    
def get_chat_content_for_token(username: str, chat_id: str):
    """
    Get the content of a specific chat.
    
    Args:
        username: The username of the chat owner
        chat_id: The ID of the chat to retrieve
        
    Returns:
        The chat content as a list of messages
    """
    file_path = f"{base_path_for_chat}/{username}/Json/{chat_id}.json"
    
    # Check if file exists
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail=f"Chat {chat_id} not found")
        
    chat_content = userchats.read_json_file_for_chat_history_Token_count(file_path)
    if chat_content is None:
        raise HTTPException(status_code=500, detail=f"Error reading chat {chat_id}")
    
    chat_Data = []
    temp_dict = {}
    for i in chat_content:
        temp_dict = {}
        temp_dict['response_id'] = i.get("response_id", "")
        temp_dict['user_message'] = i.get("user_message", "")
        temp_dict['reasioning'] = i.get("reasioning", "")
        temp_dict['AI Message'] = i.get("AI Message", "")
        temp_dict['reasoning_file'] = i.get("reasoning_file", "")
        temp_dict['final_answer_file'] = i.get("final_answer_file", "")
        chat_Data.append(temp_dict)
    return chat_Data

