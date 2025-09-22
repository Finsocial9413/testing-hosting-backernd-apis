
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(os.path.abspath(__file__))))))

from common_import import *

def get_user_account_positions(user_id, user_secret, account_id):
    """
    Get all positions for a specific account
    
    Args:
        user_id (str): User ID for the SnapTrade user
        user_secret (str): User secret for the SnapTrade user
        account_id (str): Account ID to get positions for
    
    Returns:
        list: List of positions in the account
    """
    
    try:
        response = snaptradeconfig.account_information.get_user_account_positions(
            user_id=user_id,
            user_secret=user_secret,
            account_id=account_id
        )
        return response.body
    except Exception as e:
        print(f"Error getting account positions for {account_id}: {e}")
        return []

def get_all_accounts_positions(user_id, user_secret):
    """
    Get positions for all accounts belonging to a user
    
    Args:
        user_id (str): User ID for the SnapTrade user
        user_secret (str): User secret for the SnapTrade user
    
    Returns:
        dict: Dictionary mapping account IDs to their positions
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
        
        # Get positions for each account
        all_positions = {}
        for account in accounts:
            account_id = account.get('id')
            account_name = account.get('name', f"Account {account_id}")
            
            if account_id:
                positions = get_user_account_positions(user_id, user_secret, account_id)
                if positions:
                    all_positions[account_id] = {
                        'name': account_name,
                        'positions': positions
                    }
        
        return all_positions
        
    except Exception as e:
        print(f"Error getting all account positions: {e}")
        return {}


def analyze_positions(positions):
    """
    Analyze positions and provide insights
    
    Args:
        positions (list): List of position objects
    
    Returns:
        dict: Analysis results
    """
    if not positions:
        return {}
    
    analysis = {
        'total_positions': len(positions),
        'profitable_positions': 0,
        'losing_positions': 0,
        'sectors': {},
        'asset_types': {},
        'exchanges': {},
        'currencies': {},
        'largest_position': None,
        'smallest_position': None,
        'total_unrealized_pnl': 0
    }
    
    position_values = []
    
    for position in positions:
        # Calculate position value
        try:
            quantity = float(position.get('quantity', 0))
            price = float(position.get('price', 0))
            position_value = quantity * price
            position_values.append((position, position_value))
        except (ValueError, TypeError):
            position_value = 0
        
        # Analyze P&L
        unrealized_pnl = position.get('unrealized_pnl', {})
        if isinstance(unrealized_pnl, dict):
            pnl_amount = unrealized_pnl.get('amount', 0)
        else:
            pnl_amount = unrealized_pnl
        
        try:
            pnl_float = float(pnl_amount)
            analysis['total_unrealized_pnl'] += pnl_float
            
            if pnl_float > 0:
                analysis['profitable_positions'] += 1
            elif pnl_float < 0:
                analysis['losing_positions'] += 1
        except (ValueError, TypeError):
            pass
        
        # Analyze symbol details
        symbol = position.get('symbol', {})
        if isinstance(symbol, dict):
            # Asset type
            asset_type = symbol.get('type', {})
            if isinstance(asset_type, dict):
                type_code = asset_type.get('code', 'Unknown')
                analysis['asset_types'][type_code] = analysis['asset_types'].get(type_code, 0) + 1
            
            # Exchange
            exchange = symbol.get('exchange', {})
            if isinstance(exchange, dict):
                exchange_name = exchange.get('name', 'Unknown')
                analysis['exchanges'][exchange_name] = analysis['exchanges'].get(exchange_name, 0) + 1
            
            # Currency
            currency = symbol.get('currency', {})
            if isinstance(currency, dict):
                currency_code = currency.get('code', 'Unknown')
                analysis['currencies'][currency_code] = analysis['currencies'].get(currency_code, 0) + 1
    
    # Find largest and smallest positions
    if position_values:
        position_values.sort(key=lambda x: x[1], reverse=True)
        analysis['largest_position'] = position_values[0]
        analysis['smallest_position'] = position_values[-1]
    
    return analysis


# Example usage
def get_All_positions(user_id, user_secret):    # Example user credentials
    positions_Dict = {}
    all_positions = get_all_accounts_positions(user_id, user_secret)
    if all_positions:
        # Display positions for each account
        for account_id, account_data in all_positions.items():
            account_name = account_data['name']
            positions = account_data['positions']
            
            display_account_positions(positions, account_name)
            
            # Analyze positions for this account
            analysis = analyze_positions(positions)
        
    else:
        positions_Dict['positions'] = "No positions found or failed to retrieve positions."
       
    
    # First get account list to get an account ID
    try:
        accounts_response = snaptradeconfig.account_information.list_user_accounts(
            user_id=user_id,
            user_secret=user_secret
        )
        accounts = accounts_response.body
  
        for i in accounts:
            temp = {}
            first_account_id = i.get('id')
            first_account_name = i.get('name', 'First Account')

            if first_account_id:
                positions = get_user_account_positions(user_id, user_secret, first_account_id)
                temp['account_name'] = first_account_name
                temp['account_id'] = first_account_id
                
                if positions:
                    temp['positions'] = positions
                else:
                    temp['positions'] = "No positions found."
                
                positions_Dict[first_account_name] = temp
            
            else:
                temp['positions'] = "No account ID found."
              
        else:
            positions_Dict['positions'] = "No Positions found."
        
        return positions_Dict
            
    except Exception as e:
        print(f"Error in example: {e}")