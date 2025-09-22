from agno.tools import Toolkit
from agno.utils.log import logger
import requests
import os
import json

class TelegramToolkit(Toolkit):
    """
    A toolkit that provides functionality to send messages to Telegram
    with automatic chat ID detection and storage.
    """

    def __init__(self, bot_token: str = None, chat_id: str = None, **kwargs):
        super().__init__(name="telegram_toolkit", tools=[
            self.send_to_telegram, 
            self.setup_telegram_chat,
            self.get_available_chats
        ], **kwargs)
        
        # Get bot token from environment variables or parameters
        self.bot_token = bot_token or os.getenv('TELEGRAM_BOT_TOKEN')
        self.chat_id = chat_id or os.getenv('TELEGRAM_CHAT_ID')
        self.config_file = "telegram_config.json"
        self.bot_link = "https://t.me/HindAI_FinSocial_bot"
        
        if not self.bot_token:
            logger.warning("Telegram bot token not provided. Set TELEGRAM_BOT_TOKEN environment variable.")
        
        # Try to load saved configuration
        self._load_config()
        
        # If no chat ID is configured, try to auto-detect
        if not self.chat_id and self.bot_token:
            self._auto_detect_chat_id()

    def _load_config(self):
        """Load saved Telegram configuration from file."""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    if not self.chat_id and 'chat_id' in config:
                        self.chat_id = config['chat_id']
                        logger.info(f"Loaded chat ID from config: {self.chat_id}")
        except Exception as e:
            logger.warning(f"Could not load Telegram config: {e}")

    def _save_config(self):
        """Save Telegram configuration to file."""
        try:
            config = {'chat_id': self.chat_id}
            with open(self.config_file, 'w') as f:
                json.dump(config, f)
            logger.info("Telegram configuration saved.")
        except Exception as e:
            logger.warning(f"Could not save Telegram config: {e}")

    def _get_user_info(self, chat_id):
        """Get user information for the given chat ID."""
        try:
            url = f"https://api.telegram.org/bot{self.bot_token}/getChat"
            response = requests.get(url, params={'chat_id': chat_id}, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data['ok']:
                    chat = data['result']
                    user_info = {
                        'id': chat['id'],
                        'type': chat['type'],
                        'first_name': chat.get('first_name', 'Unknown'),
                        'last_name': chat.get('last_name', ''),
                        'username': chat.get('username', 'No username'),
                        'title': chat.get('title', '')
                    }
                    return user_info
        except Exception as e:
            logger.warning(f"Could not get user info: {e}")
        
        return None

    def _print_user_info(self, chat_id):
        """Print user information to console."""
        user_info = self._get_user_info(chat_id)
        if user_info:
            print(f"\n--- USER INFO ---")
            print(f"Chat ID: {user_info['id']}")
            print(f"Type: {user_info['type']}")
            print(f"Name: {user_info['first_name']} {user_info['last_name']}".strip())
            print(f"Username: @{user_info['username']}")
            if user_info['title']:
                print(f"Group Title: {user_info['title']}")
            print(f"----------------\n")
        else:
            print(f"\n--- USER INFO ---")
            print(f"Chat ID: {chat_id}")
            print(f"Could not retrieve detailed user info")
            print(f"----------------\n")

    def _find_chat_id_by_username(self, target_username):
        """Find chat ID by username or user identifier."""
        try:
            # Clean up the username - remove @ if present
            clean_username = target_username.strip().lower()
            if clean_username.startswith('@'):
                clean_username = clean_username[1:]
            
            url = f"https://api.telegram.org/bot{self.bot_token}/getUpdates"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if data['result']:
                    # Search through all messages to find matching user
                    for update in data['result']:
                        if 'message' in update:
                            chat = update['message']['chat']
                            from_user = update['message'].get('from', {})
                            
                            # Check various identifiers
                            chat_username = chat.get('username', '').lower()
                            from_username = from_user.get('username', '').lower()
                            chat_id_str = str(chat['id'])
                            first_name = chat.get('first_name', '').lower()
                            last_name = chat.get('last_name', '').lower()
                            
                            # Match by username, chat ID, or name
                            if (clean_username == chat_username or 
                                clean_username == from_username or 
                                clean_username == chat_id_str or
                                clean_username in first_name or
                                clean_username in last_name):
                                return str(chat['id'])
                
        except Exception as e:
            logger.warning(f"Error finding chat ID for username {target_username}: {e}")
        
        return None

    def _check_user_started_bot(self, chat_id):
        """Check if user has started the bot by sending a test message."""
        try:
            url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
            payload = {
                'chat_id': chat_id,
                'text': 'Bot connection test'
            }
            response = requests.post(url, json=payload, timeout=10)
            
            if response.status_code == 200:
                return True
            else:
                error_data = response.json()
                error_msg = error_data.get('description', '').lower()
                if 'chat not found' in error_msg or 'bot was blocked' in error_msg:
                    return False
                return True  # Other errors might still mean the user started the bot
        except:
            return False

    def _auto_detect_chat_id(self):
        """Automatically detect chat ID from recent messages."""
        try:
            url = f"https://api.telegram.org/bot{self.bot_token}/getUpdates"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if data['result']:
                    # Get the most recent message
                    latest_update = data['result'][-1]
                    if 'message' in latest_update:
                        chat = latest_update['message']['chat']
                        detected_chat_id = str(chat['id'])
                        
                        # Auto-select the most recent private chat or first available chat
                        if chat['type'] == 'private' or not self.chat_id:
                            self.chat_id = detected_chat_id
                            self._save_config()
                            
                            chat_name = chat.get('first_name', chat.get('title', 'Unknown'))
                            logger.info(f"Auto-detected and saved chat ID: {self.chat_id} ({chat_name})")
                            return True
                            
        except Exception as e:
            logger.warning(f"Auto-detection failed: {e}")
        
        return False

    def setup_telegram_chat(self, instruction: str = "") -> str:
        """
        Interactive setup for Telegram chat. Call this when user wants to configure Telegram.
        
        Args:
            instruction (str): User instruction about setting up Telegram
            
        Returns:
            str: Setup instructions and status
        """
        if not self.bot_token:
            return """Telegram Bot Token Missing
            
To set up Telegram integration:

1. Create a bot:
   - Message @BotFather on Telegram
   - Send /newbot command
   - Follow the instructions
   - Copy the bot token

2. Add token to .env file:
   TELEGRAM_BOT_TOKEN=your_bot_token_here

3. Restart the application"""

        # Try to get available chats
        try:
            url = f"https://api.telegram.org/bot{self.bot_token}/getUpdates"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if data['result']:
                    chats = []
                    for update in data['result']:
                        if 'message' in update:
                            chat = update['message']['chat']
                            chat_info = {
                                'id': str(chat['id']),
                                'type': chat['type'],
                                'name': chat.get('first_name') or chat.get('title', 'Unknown')
                            }
                            if chat_info not in chats:
                                chats.append(chat_info)
                    
                    if chats:
                        # Auto-select the first private chat or any available chat
                        selected_chat = None
                        for chat in chats:
                            if chat['type'] == 'private':
                                selected_chat = chat
                                break
                        
                        if not selected_chat:
                            selected_chat = chats[0]
                        
                        self.chat_id = selected_chat['id']
                        self._save_config()
                        
                        return f"""Telegram Setup Complete!
                        
Selected chat: {selected_chat['name']} ({selected_chat['type']})
Chat ID: {selected_chat['id']}

You can now send messages to Telegram! Try saying:
- "Send this to Telegram"
- "Share on Telegram chat"""
                    
                else:
                    return f"""No messages found
                    
To complete setup:
1. Go to: {self.bot_link}
2. Press /start to begin chatting with the bot
3. Ask me to set up Telegram again

Your bot should respond after you press /start."""
                    
            else:
                return f"Bot API Error: {response.status_code}\n\nPlease check your bot token."
                
        except Exception as e:
            return f"Setup Error: {e}"

    def get_available_chats(self, query: str = "") -> str:
        """
        Shows available Telegram chats that the bot can send messages to.
        
        Returns:
            str: List of available chats
        """
        if not self.bot_token:
            return "Telegram bot token not configured."
        
        try:
            url = f"https://api.telegram.org/bot{self.bot_token}/getUpdates"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if data['result']:
                    chats = {}
                    for update in data['result']:
                        if 'message' in update:
                            chat = update['message']['chat']
                            chat_id = str(chat['id'])
                            chat_name = chat.get('first_name') or chat.get('title', 'Unknown')
                            chat_type = chat['type']
                            chats[chat_id] = f"{chat_name} ({chat_type})"
                    
                    if chats:
                        result = "Available Telegram Chats:\n\n"
                        for chat_id, chat_info in chats.items():
                            current = " <- Current" if chat_id == self.chat_id else ""
                            result += f"• {chat_info}{current}\n"
                        
                        return result
                    else:
                        return "No chats found. Send a message to your bot first."
                else:
                    return "No messages found. Send a message to your bot to see available chats."
            else:
                return f"Error accessing Telegram API: {response.status_code}"
                
        except Exception as e:
            return f"Error getting chats: {e}"

    def send_to_telegram(self, message: str, username: str = None) -> str:
        """
        Sends the given message to a Telegram chat when specified in the input prompt.
        
        Args:
            message (str): The message text to send to Telegram chat.
            username (str): The username to send the message to (required).
            
        Returns:
            str: A confirmation message or error message.
        """
        # If username is not provided, ask for it
        if not username:
            return """Username Required
            
Please specify which username you want to send the message to.
Example: "Send 'Hello' to telegram user @john_doe"
            
Or ask me to "set up telegram" to configure a default chat."""

        if not self.bot_token:
            return self.setup_telegram_chat()
        
        # Find the target chat ID based on username
        target_chat_id = self._find_chat_id_by_username(username)
        
        if not target_chat_id:
            return f"""User '{username}' not found
            
The user may not have started the bot yet. Please ask them to:
1. Go to: {self.bot_link}
2. Press /start to begin chatting with the bot
3. Then try sending the message again

Note: I can only send messages to users who have interacted with the bot."""

        # Print user info every time
        self._print_user_info(target_chat_id)
        
        # Check if user has started the bot
        if not self._check_user_started_bot(target_chat_id):
            return f"""User has not started the bot yet!

Please ask the user to:
1. Go to: {self.bot_link}
2. Press /start to begin chatting with the bot
3. Then try sending the message again"""
        
        try:
            # Telegram Bot API URL
            url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
            
            # Prepare the payload - use target_chat_id instead of self.chat_id
            payload = {
                'chat_id': target_chat_id,
                'text': message,
                'parse_mode': 'Markdown'  # Optional: allows for formatted text
            }
            
            logger.info(f"Sending message to Telegram user: {username} (Chat ID: {target_chat_id})")
            
            # Send the message
            response = requests.post(url, json=payload, timeout=10)
            
            if response.status_code == 200:
                logger.info("Message sent successfully to Telegram.")
                return f"Message sent successfully to {username} on Telegram!\n\nCheck your Telegram app"
            else:
                error_data = response.json()
                error_msg = error_data.get('description', 'Unknown error')
                
                # Handle common errors
                if 'chat not found' in error_msg.lower():
                    return f"""Chat not found
                    
The user '{username}' may no longer be available. Please ask them to:
1. Go to: {self.bot_link}
2. Press /start to begin chatting with the bot"""
                
                logger.warning(f"Failed to send message to Telegram: {error_msg}")
                return f"Failed to send message: {error_msg}"
                
        except requests.exceptions.RequestException as e:
            logger.warning(f"Network error while sending to Telegram: {e}")
            return f"Network error: Could not connect to Telegram API"
        except Exception as e:
            logger.warning(f"Telegram message sending failed: {e}")
            return f"Error sending to Telegram: {e}"

    def send_file_to_telegram(self, file_path: str, caption: str = "", username: str = None) -> str:
        """
        Sends a file to Telegram chat (useful for sending audio files, images, etc.).
        
        Args:
            file_path (str): Path to the file to send.
            caption (str): Optional caption for the file.
            username (str): The username to send the file to (required).
            
        Returns:
            str: A confirmation message or error message.
        """
        # If username is not provided, ask for it
        if not username:
            return """Username Required
            
Please specify which username you want to send the file to.
Example: "Send the audio file to telegram user @john_doe"
            
Or ask me to "set up telegram" to configure a default chat."""
        
        if not self.bot_token:
            return "Telegram not configured. Please set up Telegram first."
        
        # Find the target chat ID based on username
        target_chat_id = self._find_chat_id_by_username(username)
        
        if not target_chat_id:
            return f"""User '{username}' not found
            
The user may not have started the bot yet. Please ask them to:
1. Go to: {self.bot_link}
2. Press /start to begin chatting with the bot
3. Then try sending the file again

Note: I can only send files to users who have interacted with the bot."""
        
        # Print user info every time
        self._print_user_info(target_chat_id)
        
        # Check if user has started the bot
        if not self._check_user_started_bot(target_chat_id):
            return f"""User has not started the bot yet!

Please ask the user to:
1. Go to: {self.bot_link}
2. Press /start to begin chatting with the bot
3. Then try sending the file again"""
        
        try:
            if not os.path.exists(file_path):
                return f"File not found: {file_path}"
            
            # Determine file type and API endpoint
            file_extension = file_path.lower().split('.')[-1]
            
            if file_extension in ['mp3', 'wav', 'ogg']:
                url = f"https://api.telegram.org/bot{self.bot_token}/sendAudio"
                file_key = 'audio'
            elif file_extension in ['jpg', 'jpeg', 'png', 'gif']:
                url = f"https://api.telegram.org/bot{self.bot_token}/sendPhoto"
                file_key = 'photo'
            elif file_extension in ['mp4', 'avi']:
                url = f"https://api.telegram.org/bot{self.bot_token}/sendVideo"
                file_key = 'video'
            else:
                url = f"https://api.telegram.org/bot{self.bot_token}/sendDocument"
                file_key = 'document'
            
            logger.info(f"Sending file {file_path} to Telegram user: {username} (Chat ID: {target_chat_id})")
            
            # Prepare the files and data - use target_chat_id instead of self.chat_id
            with open(file_path, 'rb') as file:
                files = {file_key: file}
                data = {
                    'chat_id': target_chat_id,
                    'caption': caption
                }
                
                response = requests.post(url, files=files, data=data, timeout=30)
            
            if response.status_code == 200:
                logger.info(f"File {file_path} sent successfully to Telegram.")
                return f"File sent successfully to {username} on Telegram!\n\nFile: {os.path.basename(file_path)}"
            else:
                error_data = response.json()
                error_msg = error_data.get('description', 'Unknown error')
                logger.warning(f"Failed to send file to Telegram: {error_msg}")
                return f"Failed to send file: {error_msg}"
                
        except Exception as e:
            logger.warning(f"File sending to Telegram failed: {e}")
            return f"Error sending file to Telegram: {e}"