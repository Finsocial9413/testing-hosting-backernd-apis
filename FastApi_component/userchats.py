import os
import json

def list_json_files(directory):
    """
    Walk through the directory and list all .json files.

    Args:
        directory (str): The directory to search.

    Returns:
        List of paths to .json files.
    """
    json_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.json'):
                json_files.append(os.path.join(root, file))
    return json_files

def get_markdown_file_paths(username, chat_id, task_id):
    """
    Get reasoning and final answer markdown file paths for a specific response using task_id.

    Args:
        username (str): The username
        chat_id (str): The chat ID
        task_id (str): The task ID from JSON file

    Returns:
        Tuple of (reasoning_file_path, final_answer_file_path)
    """
    base_markdown_path = f"D:/finsocial/Multi model adding for the trading/userChats/{username}/markdown"
    
    # Construct exact file paths using task_id
    reasoning_file_path = f"{base_markdown_path}/reasoning/{chat_id}/{task_id}.md"
    final_answer_file_path = f"{base_markdown_path}/final_answer/{chat_id}/{task_id}.md"
    
    # Check if files exist and return paths or empty string
    reasoning_path = reasoning_file_path if os.path.exists(reasoning_file_path) else ""
    final_answer_path = final_answer_file_path if os.path.exists(final_answer_file_path) else ""
    
    return reasoning_path, final_answer_path

def get_userchats(directory_to_search):
    json_files = list_json_files(directory_to_search)
    print(f"Found {len(json_files)} JSON files in the directory.")
    chats_list = []
    for json_file in json_files:
        # Read the content of each JSON file
        chat_content = read_json_file(json_file)
        if chat_content and len(chat_content) > 0:
            # Get the first user message from the chat
            first_message = chat_content[0]['user_message']
            # Get the chat ID from the filename
            chat_id = os.path.basename(json_file).replace('.json', '')
            
            chats_list.append({
                "chat_id": chat_id,
                "message": first_message
            })
    
    return chats_list

def read_json_file(file_path):
    """
    Reads the content of a JSON file.

    Args:
        file_path (str): The path to the JSON file.

    Returns:
        The parsed content of the JSON file (dict or list).
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            json_data = json.load(file)
            chat = []
            
            # Extract username and chat_id from file path
            path_parts = file_path.replace('\\', '/').split('/')
            username = path_parts[-3]  # Extract username from path
            chat_id = os.path.basename(file_path).replace('.json', '')
            
            for i in json_data:
                temp = {}
                temp['response_id'] = i['response_id']
                temp['user_message'] = i['user message']
                
                if len(i['Main_reasoning_translated']) > 2:
                    temp['reasioning'] = i['Main_reasoning_translated']
                else:
                    temp['reasioning'] = i['Main_reasoning']
                    
                if len(i['Translated AI Message']) > 2:
                    temp['AI Message'] = i['Translated AI Message']
                else:
                    temp['AI Message'] = i["AI Message"]
                
                # Use task_id instead of response_id to find markdown file paths
                task_id = i.get('task_id', i['response_id'])  # Fallback to response_id if task_id not found
                reasoning_path, final_answer_path = get_markdown_file_paths(
                    username, chat_id, task_id
                )
                temp['reasoning_file'] = reasoning_path
                temp['final_answer_file'] = final_answer_path
                
                chat.append(temp)
            return chat
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        return None

def read_json_file_for_chat_history_Token_count(file_path):
    """
    Reads the content of a JSON file.

    Args:
        file_path (str): The path to the JSON file.

    Returns:
        The parsed content of the JSON file (dict or list).
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            json_data = json.load(file)
            chat = []
            
            # Extract username and chat_id from file path
            path_parts = file_path.replace('\\', '/').split('/')
            username = path_parts[-3]  # Extract username from path
            chat_id = os.path.basename(file_path).replace('.json', '')
            
            for i in json_data:
                temp = {}
                temp['response_id'] = i['response_id']
                temp['reasioning'] = i['Main_reasoning']
                temp['AI Message'] = i["AI Message"]
                
                if len(i['Translated user message']) > 1:
                    temp['user_message'] = i['Translated user message']
                else:
                    temp['user_message'] = i['user message']
                
                # Use task_id instead of response_id to find markdown file paths
                task_id = i.get('task_id', i['response_id'])  # Fallback to response_id if task_id not found
                reasoning_path, final_answer_path = get_markdown_file_paths(
                    username, chat_id, task_id
                )
                temp['reasoning_file'] = reasoning_path
                temp['final_answer_file'] = final_answer_path
                
                chat.append(temp)
            return chat
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        return None


