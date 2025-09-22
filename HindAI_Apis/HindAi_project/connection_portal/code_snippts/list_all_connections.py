
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(os.path.abspath(__file__))))))

from common_import import *

# List all brokerage connections for a user
def list_brokerage_connections(user_id, user_secret):
    """
    List all brokerage authorizations/connections for a specific user
    
    Args:
        user_id (str): User ID for the SnapTrade user
        user_secret (str): User secret for the SnapTrade user
    
    Returns:
        list: List of brokerage authorization objects
    """
    
    try:
        response = snaptradeconfig.connections.list_brokerage_authorizations(
            user_id=user_id,
            user_secret=user_secret
        )
        return response.body
    except Exception as e:
        print(f"Error listing brokerage connections: {e}")
        return None


# Get connection summary statistics
def get_connection_summary(connections):
    """
    Get summary statistics about user's brokerage connections
    
    Args:
        connections (list): List of brokerage authorization objects
    
    Returns:
        dict: Summary statistics
    """
    if not connections:
        return {"total": 0, "active": 0, "inactive": 0, "brokerages": []}
    
    total = len(connections)
    active = sum(1 for conn in connections if conn.get('status') == 'ACTIVE')
    inactive = total - active
    
    brokerages = list(set(
        conn.get('brokerage', {}).get('name', 'Unknown') 
        for conn in connections
    ))
    
    return {
        "total": total,
        "active": active,
        "inactive": inactive,
        "brokerages": brokerages
    }

# Example usage
def list_all_connections(user_id, user_secret):

    print("Fetching brokerage connections...")
    connections = list_brokerage_connections(user_id, user_secret)
    if connections is not None:        
        # Display summary statistics
        summary = get_connection_summary(connections)

        return connections
    else:
        return "Failed to retrieve brokerage connections"