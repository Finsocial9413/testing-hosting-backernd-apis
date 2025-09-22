
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(os.path.abspath(__file__))))))

from common_import import *

# Generate connection portal URL for user to link their brokerage account
def generate_connection_portal(user_id, user_secret, immediate_redirect=True, custom_redirect=None, reconnect=None, connection_type=None, connection_portal_version="v3"):
    """
    Generate a secure URL for users to connect their brokerage accounts
    
    Args:
        user_id (str): User ID for the SnapTrade user
        user_secret (str): User secret for the SnapTrade user
        immediate_redirect (bool): Whether to redirect immediately after connection
        custom_redirect (str): Custom redirect URL after connection
        reconnect (str): UUID of existing connection to reconnect
        connection_type (str): Type of connection (read/trade)
        connection_portal_version (str): Version of connection portal to use
    
    Returns:
        dict: Response containing the redirect URL
    """
    
    # Build the request parameters
    params = {
        "user_id": user_id,
        "user_secret": user_secret,
        "immediate_redirect": immediate_redirect,
        "connection_portal_version": connection_portal_version
    }
    
    # Add optional parameters if provided
    if custom_redirect:
        params["custom_redirect"] = custom_redirect
    if reconnect:
        params["reconnect"] = reconnect
    if connection_type:
        params["connection_type"] = connection_type
    
    try:
        response = snaptradeconfig.authentication.login_snap_trade_user(**params)
        return response.body
    except Exception as e:
        print(f"Error generating connection portal: {e}")
        return None

# Example usage
def connection_portal(username, user_secret):
    # Example with basic parameters
    user_id = username
    user_secret = user_secret  # Use actual user secret

    # Example with custom redirect URL
    print("\n" + "="*50)
    print("Example with custom redirect:")
    
    custom_result = generate_connection_portal(
        user_id=user_id,
        user_secret=user_secret,
        immediate_redirect=False,
        custom_redirect="https://finsocial.tech/",
        connection_type="trade"
    )
    
    if custom_result:
        print("Custom connection portal generated:")
        return custom_result