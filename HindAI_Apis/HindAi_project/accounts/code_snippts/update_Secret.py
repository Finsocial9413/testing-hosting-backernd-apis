import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(os.path.abspath(__file__))))))

from common_import import *
# Registering a new user
def update_snaptrade_secret(username, user_secret):
    """Update the secret for a Snaptrade user"""
    try:
        # Assuming snaptradeconfig has a method to update user secret
        response = snaptradeconfig.authentication.reset_snap_trade_user_secret(
            user_id=username,
            user_secret=user_secret
        )
        return response
    except Exception as e:
        print(f"Error updating Snaptrade user secret: {e}")
        return None