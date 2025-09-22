import os
import sys
import django

import asyncio
from asgiref.sync import sync_to_async
# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'HindAi_project.settings')
django.setup()

from HindAi_users.models import HindAIUser

# Now you can use the models in your code
# Example usage:



async def get_user_connections(user):
    """
    Get all active platform connections for a user
    """
    try:
        user = await sync_to_async(HindAIUser.objects.get)(username=user)
        return True
    except HindAIUser.DoesNotExist:
        return False

