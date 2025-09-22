
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(os.path.abspath(__file__))))))

from common_import import *

# Delete a specific brokerage connection
def delete_brokerage_connection(user_id, user_secret, authorization_id):
    """
    Remove/delete a brokerage authorization for a specific user
    
    Args:
        user_id (str): User ID for the SnapTrade user
        user_secret (str): User secret for the SnapTrade user
        authorization_id (str): ID of the brokerage authorization to remove
    
    Returns:
        dict: Response from the API (empty dict on success)
    """
    
    try:
        response = snaptradeconfig.connections.remove_brokerage_authorization(
            user_id=user_id,
            user_secret=user_secret,
            authorization_id=authorization_id
        )
        return response.body
    except Exception as e:
        print(f"Error deleting brokerage connection: {e}")
        return None

# Example usage
def delete_speacific_connections(user_id, user_secret, authorization_id):
    """Example usage of the delete_brokerage_connection function"""

 
    result = delete_brokerage_connection(user_id, user_secret, authorization_id)

    if result is not None:
        return "Connection deleted successfully"
    else:
        return "Failed to delete connection"
