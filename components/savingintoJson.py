import os
import json
from datetime import datetime
import uuid

def save_message_to_json(username: str, chat_id: str, message: str, base_path) -> str:
    user_dir = os.path.join(base_path, username, "Json")
    os.makedirs(user_dir, exist_ok=True)
    file_path = os.path.join(user_dir, f"{chat_id}.json")

    # Generate a unique response ID
    response_id = str(uuid.uuid4())

    # Define the default structure for a new entry
    new_entry = {
        "response_id": response_id,
        "user message": message,
        "Translated user message": '',
        "AI Message": "",
        "time": datetime.now().isoformat()
    }

    try:
        with open(file_path, "r") as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        data = []

    data.append(new_entry)

    with open(file_path, "w") as f:
        json.dump(data, f, indent=4)
    
    return response_id

def update_json_entry(username: str, chat_id: str, response_id: str, field: str, content: str, base_path) -> bool:
    """
    Update a specific field in an existing JSON entry identified by response_id.
    
    Args:
        username: The username of the user
        chat_id: The chat ID
        response_id: The unique ID of the entry to update
        field: The field to update ('reasioning', 'AI Message', etc.)
        content: The content to add to the field
        
    Returns:
        bool: True if the update was successful, False otherwise
    """
    user_dir = os.path.join(base_path, username, "Json")
    file_path = os.path.join(user_dir, f"{chat_id}.json")
    
    if not os.path.exists(file_path):
        return False
    
    try:
        with open(file_path, "r") as f:
            data = json.load(f)
        
        # Find the entry with matching response_id
        found = False
        for entry in data:
            if entry.get("response_id") == response_id:
                entry[field] = content
                found = True
                break
                
        if not found:
            return False
            
        # Save the updated data
        with open(file_path, "w") as f:
            json.dump(data, f, indent=4)
        
        return True
        
    except Exception as e:
        print(f"Error updating JSON: {e}")
        return False