
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common_import import *

# Refresh a specific brokerage authorization
def refresh_brokerage_authorization(user_id, user_secret, authorization_id):
    """
    Refresh/update a brokerage authorization for a specific user
    
    Args:
        user_id (str): User ID for the SnapTrade user
        user_secret (str): User secret for the SnapTrade user
        authorization_id (str): ID of the brokerage authorization to refresh
    
    Returns:
        dict: Response from the API containing updated authorization details
    """
    
    try:
        response = snaptradeconfig.connections.refresh_brokerage_authorization(
            user_id=user_id,
            user_secret=user_secret,
            authorization_id=authorization_id
        )
        return response.body
    except Exception as e:
        print(f"Error refreshing brokerage authorization: {e}")
        return None

# Get detailed information about a specific brokerage authorization
def get_brokerage_authorization_details(user_id, user_secret, authorization_id):
    """
    Get detailed information about a specific brokerage authorization
    
    Args:
        user_id (str): User ID for the SnapTrade user
        user_secret (str): User secret for the SnapTrade user
        authorization_id (str): ID of the brokerage authorization to get details for
    
    Returns:
        dict: Detailed authorization information
    """
    
    try:
        # First get all connections to find the specific one
        response = snaptradeconfig.connections.list_brokerage_authorizations(
            user_id=user_id,
            user_secret=user_secret
        )
        connections = response.body
        
        # Find the specific authorization
        for connection in connections:
            if connection.get('id') == authorization_id:
                return connection
        
        print(f"Authorization ID {authorization_id} not found")
        return None
        
    except Exception as e:
        print(f"Error getting brokerage authorization details: {e}")
        return None

# Display detailed authorization information
def display_authorization_details(authorization):
    """
    Display brokerage authorization details in a readable format
    
    Args:
        authorization (dict): Authorization object
    """
    if not authorization:
        print("No authorization details available.")
        return
    
    print("\nBrokerage Authorization Details:")
    print("=" * 50)
    
    print(f"ID: {authorization.get('id', 'N/A')}")
    print(f"Name: {authorization.get('name', 'N/A')}")
    print(f"Type: {authorization.get('type', 'N/A')}")
    print(f"Status: {authorization.get('status', 'N/A')}")
    
    # Display brokerage info if available
    if 'brokerage' in authorization:
        brokerage = authorization['brokerage']
        print(f"Brokerage Name: {brokerage.get('name', 'N/A')}")
        print(f"Brokerage ID: {brokerage.get('id', 'N/A')}")
        print(f"Brokerage Slug: {brokerage.get('slug', 'N/A')}")
        
        if 'logo_url' in brokerage:
            print(f"Brokerage Logo: {brokerage['logo_url']}")
    
    # Display timestamps
    if 'created_date' in authorization:
        print(f"Created Date: {authorization['created_date']}")
    
    if 'updated_date' in authorization:
        print(f"Updated Date: {authorization['updated_date']}")
    
    # Display additional metadata if available
    if 'metadata' in authorization:
        print(f"Metadata: {authorization['metadata']}")
    
    print("-" * 50)

# Refresh and display updated authorization details
def refresh_and_display_authorization(user_id, user_secret, authorization_id):
    """
    Refresh a brokerage authorization and display the updated details
    
    Args:
        user_id (str): User ID for the SnapTrade user
        user_secret (str): User secret for the SnapTrade user
        authorization_id (str): ID of the brokerage authorization to refresh
    """
    
    print(f"Refreshing brokerage authorization: {authorization_id}")
    print("-" * 50)
    
    # Refresh the authorization
    refreshed_auth = refresh_brokerage_authorization(user_id, user_secret, authorization_id)
    
    if refreshed_auth:
        print("✓ Authorization refreshed successfully")
        display_authorization_details(refreshed_auth)
        
        # Also show raw response for debugging
        print("\nRaw Response:")
        print("=" * 50)
        pprint(refreshed_auth)
    else:
        print("✗ Failed to refresh authorization")

# Example usage
def get_speacific_connection_details(user_id,user_secret, authorization_id):
    """Get specific connection details for a user"""
    # Ensure snaptradeconfig is properly initialized
    # Example user credentials
    user_id = user_id
    user_secret = user_secret
    authorization_id = authorization_id


    current_details = get_brokerage_authorization_details(user_id, user_secret, authorization_id)
    if current_details:
        display_authorization_details(current_details)
    
    return current_details