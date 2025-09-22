import random
def generate_unique_id() -> str:
    """Generate a unique 10-digit id as a string."""
    chat_id = str(random.randint(1000000000, 9999999999))
    if len(chat_id) != 10:
        chat_id = generate_unique_id()
    return chat_id

import re

# Sanitize the chat_id to remove invalid characters
def sanitize_chat_id(chat_id: str) -> str:
    return re.sub(r'[<>:"/\\|?*]', '_', chat_id)  # Replace invalid characters with '_'
