
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

# Delete all brokerage connections for a user
def delete_all_brokerage_connections(user_id, user_secret, confirm=False):
    """
    Remove all brokerage authorizations for a specific user
    
    Args:
        user_id (str): User ID for the SnapTrade user
        user_secret (str): User secret for the SnapTrade user
        confirm (bool): Safety confirmation to prevent accidental deletion
    
    Returns:
        dict: Summary of deletion results
    """
    
    if not confirm:
        print("WARNING: This will delete ALL brokerage connections for the user!")
        print("Set confirm=True to proceed with deletion.")
        return None
    
    # First, get all existing connections
    try:
        response = snaptradeconfig.connections.list_brokerage_authorizations(
            user_id=user_id,
            user_secret=user_secret
        )
        connections = response.body
    except Exception as e:
        print(f"Error listing connections: {e}")
        return None
    
    if not connections:
        print("No connections found to delete.")
        return {"deleted": 0, "failed": 0, "total": 0}
    
    # Delete each connection
    deleted_count = 0
    failed_count = 0
    failed_ids = []
    
    print(f"Deleting {len(connections)} connection(s)...")
    
    for connection in connections:
        connection_id = connection.get('id')
        if connection_id:
            result = delete_brokerage_connection(user_id, user_secret, connection_id)
            if result is not None:
                deleted_count += 1
                print(f"✓ Deleted connection: {connection.get('name', connection_id)}")
            else:
                failed_count += 1
                failed_ids.append(connection_id)
                print(f"✗ Failed to delete connection: {connection.get('name', connection_id)}")
    
    return {
        "deleted": deleted_count,
        "failed": failed_count,
        "total": len(connections),
        "failed_ids": failed_ids
    }

# Interactive deletion with user confirmation
def interactive_delete_connection(user_id, user_secret):
    """
    Interactive function to list and delete connections with user confirmation
    
    Args:
        user_id (str): User ID for the SnapTrade user
        user_secret (str): User secret for the SnapTrade user
    """
    
    # Get all connections first
    try:
        response = snaptradeconfig.connections.list_brokerage_authorizations(
            user_id=user_id,
            user_secret=user_secret
        )
        connections = response.body
    except Exception as e:
        print(f"Error listing connections: {e}")
        return
    
    if not connections:
        print("No brokerage connections found.")
        return
    
    # Display all connections
    print(f"\nFound {len(connections)} brokerage connection(s):")
    print("=" * 60)
    
    for i, connection in enumerate(connections, 1):
        print(f"{i}. {connection.get('name', 'Unknown')} (ID: {connection.get('id', 'N/A')})")
        print(f"   Brokerage: {connection.get('brokerage', {}).get('name', 'Unknown')}")
        print(f"   Status: {connection.get('status', 'Unknown')}")
        print()
    
    # Get user choice
    try:
        choice = input("Enter connection number to delete (or 'all' for all connections, 'q' to quit): ").strip()
        
        if choice.lower() == 'q':
            print("Cancelled.")
            return
        
        if choice.lower() == 'all':
            confirm = input("Are you sure you want to delete ALL connections? (yes/no): ").strip().lower()
            if confirm == 'yes':
                result = delete_all_brokerage_connections(user_id, user_secret, confirm=True)
                if result:
                    print(f"\nDeletion Summary:")
                    print(f"Total connections: {result['total']}")
                    print(f"Successfully deleted: {result['deleted']}")
                    print(f"Failed to delete: {result['failed']}")
            else:
                print("Cancelled.")
            return
        
        # Single connection deletion
        connection_num = int(choice) - 1
        if 0 <= connection_num < len(connections):
            connection = connections[connection_num]
            connection_id = connection.get('id')
            connection_name = connection.get('name', 'Unknown')
            
            confirm = input(f"Are you sure you want to delete '{connection_name}'? (yes/no): ").strip().lower()
            if confirm == 'yes':
                result = delete_brokerage_connection(user_id, user_secret, connection_id)
                if result is not None:
                    print(f"✓ Successfully deleted connection: {connection_name}")
                else:
                    print(f"✗ Failed to delete connection: {connection_name}")
            else:
                print("Cancelled.")
        else:
            print("Invalid connection number.")
    
    except ValueError:
        print("Invalid input. Please enter a number.")
    except KeyboardInterrupt:
        print("\nCancelled.")

# Example usage
def delete_all_connections_complete(user_id, user_secret):
    """Example usage of the delete_all_brokerage_connections function"""
 # Use actual user secret

    # Automatically delete all connections
    result = delete_all_brokerage_connections(user_id, user_secret, confirm=True)
    if result:
        return { "Total connections": result['total'], "Successfully deleted": result['deleted'], "Failed to delete": result['failed'] }
    else:
        return {"error": "No connections found or deletion failed."}
