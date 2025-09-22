import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common_import import *

def get_user_account_orders(user_id, user_secret, account_id, state=None, days=None):
    """
    Get all orders for a specific account
    
    Args:
        user_id (str): User ID for the SnapTrade user
        user_secret (str): User secret for the SnapTrade user
        account_id (str): Account ID to get orders for
        state (str, optional): Filter by order state ('all', 'open', 'executed')
        days (int, optional): Number of days to look back for orders
    
    Returns:
        list: List of orders for the account
    """
    
    try:
        # Build parameters dictionary
        params = {
            'user_id': user_id,
            'user_secret': user_secret,
            'account_id': account_id
        }
        
        if state:
            # Convert state to lowercase to match API requirements
            valid_states = ['all', 'open', 'executed']
            state_lower = state.lower()
            if state_lower in valid_states:
                params['state'] = state_lower
            else:
                print(f"Warning: Invalid state '{state}'. Valid states are: {valid_states}")
                print("Using 'all' as default state.")
                params['state'] = 'all'
        
        if days:
            params['days'] = days
            
        response = snaptradeconfig.account_information.get_user_account_orders(**params)
        return response.body
    except Exception as e:
        print(f"Error getting account orders for {account_id}: {e}")
        return []



def get_all_accounts_orders(user_id, user_secret, state=None, days=None):
    """
    Get orders for all accounts belonging to a user
    
    Args:
        user_id (str): User ID for the SnapTrade user
        user_secret (str): User secret for the SnapTrade user
        state (str, optional): Filter by order state
        days (int, optional): Number of days to look back for orders
    
    Returns:
        dict: Dictionary mapping account IDs to their orders
    """
    
    try:
        # First get all accounts for the user
        accounts_response = snaptradeconfig.account_information.list_user_accounts(
            user_id=user_id,
            user_secret=user_secret
        )
        accounts = accounts_response.body
        
        if not accounts:
            print("No accounts found for user.")
            return {}
        
        # Get orders for each account
        all_orders = {}
        for account in accounts:
            account_id = account.get('id')
            account_name = account.get('name', f"Account {account_id}")
            
            if account_id:
                orders = get_user_account_orders(user_id, user_secret, account_id, state, days)
                if orders:
                    all_orders[account_id] = {
                        'name': account_name,
                        'orders': orders
                    }
        
        return all_orders
        
    except Exception as e:
        print(f"Error getting all account orders: {e}")
        return {}

def analyze_orders(orders):
    """
    Analyze orders and provide insights
    
    Args:
        orders (list): List of order objects
    
    Returns:
        dict: Analysis results
    """
    if not orders:
        return {}
    
    analysis = {
        'total_orders': len(orders),
        'status_breakdown': {},
        'action_breakdown': {},
        'order_type_breakdown': {},
        'symbol_breakdown': {},
        'time_analysis': {
            'oldest_order': None,
            'newest_order': None
        },
        'execution_rate': 0,
        'average_order_size': 0
    }
    
    total_quantity = 0
    executed_orders = 0
    order_times = []
    
    for order in orders:
        # Status breakdown
        status = order.get('status', 'UNKNOWN')
        analysis['status_breakdown'][status] = analysis['status_breakdown'].get(status, 0) + 1
        
        # Action breakdown
        action = order.get('action', 'UNKNOWN')
        analysis['action_breakdown'][action] = analysis['action_breakdown'].get(action, 0) + 1
        
        # Order type breakdown
        order_type = order.get('order_type', 'UNKNOWN')
        analysis['order_type_breakdown'][order_type] = analysis['order_type_breakdown'].get(order_type, 0) + 1
        
        # Symbol breakdown
        symbol = order.get('symbol', {})
        symbol_name = symbol.get('symbol', 'N/A') if isinstance(symbol, dict) else str(symbol)
        analysis['symbol_breakdown'][symbol_name] = analysis['symbol_breakdown'].get(symbol_name, 0) + 1
        
        # Execution rate
        if status in ['EXECUTED', 'FILLED']:
            executed_orders += 1
        
        # Average order size
        try:
            quantity = float(order.get('quantity', 0))
            total_quantity += quantity
        except (ValueError, TypeError):
            pass
        
        # Time analysis
        created_time = order.get('created_time')
        if created_time:
            order_times.append(created_time)
    
    # Calculate execution rate
    if analysis['total_orders'] > 0:
        analysis['execution_rate'] = (executed_orders / analysis['total_orders']) * 100
    
    # Calculate average order size
    if analysis['total_orders'] > 0:
        analysis['average_order_size'] = total_quantity / analysis['total_orders']
    
    # Time analysis
    if order_times:
        analysis['time_analysis']['oldest_order'] = min(order_times)
        analysis['time_analysis']['newest_order'] = max(order_times)
    
    return analysis


def filter_orders_by_criteria(orders, symbol=None, action=None, status=None, min_quantity=None):
    """
    Filter orders by various criteria
    
    Args:
        orders (list): List of order objects
        symbol (str, optional): Filter by symbol
        action (str, optional): Filter by action (BUY/SELL)
        status (str, optional): Filter by status
        min_quantity (float, optional): Minimum quantity filter
    
    Returns:
        list: Filtered orders
    """
    filtered_orders = []
    
    for order in orders:
        # Symbol filter
        if symbol:
            order_symbol = order.get('symbol', {})
            order_symbol_name = order_symbol.get('symbol', 'N/A') if isinstance(order_symbol, dict) else str(order_symbol)
            if order_symbol_name.upper() != symbol.upper():
                continue
        
        # Action filter
        if action:
            if order.get('action', '').upper() != action.upper():
                continue
        
        # Status filter
        if status:
            if order.get('status', '').upper() != status.upper():
                continue
        
        # Quantity filter
        if min_quantity:
            try:
                order_quantity = float(order.get('quantity', 0))
                if order_quantity < min_quantity:
                    continue
            except (ValueError, TypeError):
                continue
        
        filtered_orders.append(order)
    
    return filtered_orders

# Example usage
if __name__ == "__main__":
    # Example user credentials
    user_id = "myuser1"
    user_secret = "c59995df-9148-465f-b06e-a2c628f735d5"  # Use actual user secret
    
    print("SnapTrade Account Orders Tool")
    print("=" * 80)
    
    # Get all account orders
    print("Fetching all account orders...")
    all_orders = get_all_accounts_orders(user_id, user_secret)
    
    if all_orders:
        # Display orders for each account
        for account_id, account_data in all_orders.items():
            account_name = account_data['name']
            orders = account_data['orders']
            
            
            # Analyze orders for this account
            analysis = analyze_orders(orders)
        
        # Display summary across all accounts
        
        # Raw data for debugging
        print(f"\n{'='*80}")
        print("RAW ORDERS DATA:")
        pprint(all_orders)
    else:
        print("No orders found or failed to retrieve orders.")
    
    # Example: Get orders for a specific account with filters
    print(f"\n{'='*80}")
    print("Example: Getting orders for a specific account...")
    
    # First get account list to get an account ID
    try:
        accounts_response = snaptradeconfig.account_information.list_user_accounts(
            user_id=user_id,
            user_secret=user_secret
        )
        accounts = accounts_response.body
        
        if accounts:
            first_account_id = accounts[0].get('id')
            first_account_name = accounts[0].get('name', 'First Account')
            
            if first_account_id:
                print(f"Getting orders for {first_account_name} (ID: {first_account_id})")
                
                # Get all orders
                all_orders = get_user_account_orders(user_id, user_secret, first_account_id, state='all')
                
                # Get only executed orders
                executed_orders = get_user_account_orders(user_id, user_secret, first_account_id, state='executed')
                
                # Get only open orders
                open_orders = get_user_account_orders(user_id, user_secret, first_account_id, state='open')
                
                # Get orders from last 30 days
                recent_orders = get_user_account_orders(user_id, user_secret, first_account_id, days=30)
                
                print(f"All orders: {len(all_orders)}")
                print(f"Executed orders: {len(executed_orders)}")
                print(f"Open orders: {len(open_orders)}")
                print(f"Recent orders (30 days): {len(recent_orders)}")
                
                if all_orders:
                    
                    # Show detailed view of first order
                    print(f"\nDetailed view of first order:")
                    
                    # Example filtering
                    print(f"\nFiltering examples:")
                    buy_orders = filter_orders_by_criteria(all_orders, action='BUY')
                    print(f"Buy orders: {len(buy_orders)}")
                    
                    executed_orders_filtered = filter_orders_by_criteria(all_orders, status='EXECUTED')
                    print(f"Executed orders: {len(executed_orders_filtered)}")
                else:
                    print("No orders found in this account.")
            else:
                print("No account ID found.")
        else:
            print("No accounts found.")
    except Exception as e:
        print(f"Error in example: {e}")