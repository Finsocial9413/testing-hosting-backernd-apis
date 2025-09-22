
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(os.path.abspath(__file__))))))

from common_import import *

from datetime import datetime, timedelta
import json

def get_user_account_option_positions(user_id, user_secret, account_id):
    """
    Get all option positions for a specific account
    
    Args:
        user_id (str): User ID for the SnapTrade user
        user_secret (str): User secret for the SnapTrade user
        account_id (str): Account ID to get option positions for
    
    Returns:
        list: List of option positions in the account
    """
    
    try:
        response = snaptradeconfig.options.list_option_holdings(
            user_id=user_id,
            user_secret=user_secret,
            account_id=account_id
        )
        return response.body
    except Exception as e:
        print(f"Error getting option positions for {account_id}: {e}")
        return []


def get_all_accounts_option_positions(user_id, user_secret):
    """
    Get option positions for all accounts belonging to a user
    
    Args:
        user_id (str): User ID for the SnapTrade user
        user_secret (str): User secret for the SnapTrade user
    
    Returns:
        dict: Dictionary mapping account IDs to their option positions
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
        
        # Get option positions for each account
        all_option_positions = {}
        for account in accounts:
            account_id = account.get('id')
            account_name = account.get('name', f"Account {account_id}")
            
            if account_id:
                option_positions = get_user_account_option_positions(user_id, user_secret, account_id)
                if option_positions:
                    all_option_positions[account_id] = {
                        'name': account_name,
                        'positions': option_positions
                    }
        
        return all_option_positions
        
    except Exception as e:
        print(f"Error getting all option positions: {e}")
        return {}

def analyze_option_positions(positions):
    """
    Analyze option positions and provide insights
    
    Args:
        positions (list): List of option position objects
    
    Returns:
        dict: Analysis results
    """
    if not positions:
        return {}
    
    analysis = {
        'total_positions': len(positions),
        'call_positions': 0,
        'put_positions': 0,
        'total_market_value': 0,
        'total_unrealized_pnl': 0,
        'expiration_breakdown': {},
        'strike_breakdown': {},
        'underlying_breakdown': {},
        'moneyness_breakdown': {
            'ITM': 0,  # In The Money
            'OTM': 0,  # Out of The Money
            'ATM': 0   # At The Money
        },
        'time_to_expiration': {
            'this_week': 0,
            'next_week': 0,
            'this_month': 0,
            'next_month': 0,
            'longer_term': 0
        }
    }
    
    today = datetime.now()
    
    for position in positions:
        option_symbol = position.get('option_symbol', {})
        
        if isinstance(option_symbol, dict):
            # Option type breakdown
            option_type = option_symbol.get('option_type', '').upper()
            if option_type == 'CALL':
                analysis['call_positions'] += 1
            elif option_type == 'PUT':
                analysis['put_positions'] += 1
            
            # Expiration breakdown
            exp_date = option_symbol.get('expiration_date', 'N/A')
            if exp_date != 'N/A':
                analysis['expiration_breakdown'][exp_date] = analysis['expiration_breakdown'].get(exp_date, 0) + 1
                
                # Time to expiration analysis
                try:
                    exp_date_obj = datetime.strptime(exp_date, '%Y-%m-%d')
                    days_to_exp = (exp_date_obj - today).days
                    
                    if days_to_exp <= 7:
                        analysis['time_to_expiration']['this_week'] += 1
                    elif days_to_exp <= 14:
                        analysis['time_to_expiration']['next_week'] += 1
                    elif days_to_exp <= 30:
                        analysis['time_to_expiration']['this_month'] += 1
                    elif days_to_exp <= 60:
                        analysis['time_to_expiration']['next_month'] += 1
                    else:
                        analysis['time_to_expiration']['longer_term'] += 1
                except:
                    pass
            
            # Strike breakdown
            strike = option_symbol.get('strike_price', 'N/A')
            if strike != 'N/A':
                analysis['strike_breakdown'][strike] = analysis['strike_breakdown'].get(strike, 0) + 1
            
            # Underlying breakdown
            underlying = option_symbol.get('underlying_symbol', {})
            if isinstance(underlying, dict):
                underlying_symbol = underlying.get('symbol', 'N/A')
                if underlying_symbol != 'N/A':
                    analysis['underlying_breakdown'][underlying_symbol] = analysis['underlying_breakdown'].get(underlying_symbol, 0) + 1
        
        # Market value and P&L
        try:
            quantity = float(position.get('quantity', 0))
            price = float(position.get('price', 0))
            market_value = quantity * price * 100
            analysis['total_market_value'] += market_value
            
            unrealized_pnl = position.get('unrealized_pnl', {})
            if isinstance(unrealized_pnl, dict):
                pnl_amount = float(unrealized_pnl.get('amount', 0))
                analysis['total_unrealized_pnl'] += pnl_amount
            elif unrealized_pnl:
                analysis['total_unrealized_pnl'] += float(unrealized_pnl)
        except (ValueError, TypeError):
            continue
    
    return analysis


def filter_option_positions_by_criteria(positions, option_type=None, underlying_symbol=None, days_to_expiration=None, moneyness=None):
    """
    Filter option positions by various criteria
    
    Args:
        positions (list): List of option position objects
        option_type (str, optional): Filter by option type ('CALL' or 'PUT')
        underlying_symbol (str, optional): Filter by underlying symbol
        days_to_expiration (int, optional): Filter by days to expiration (less than)
        moneyness (str, optional): Filter by moneyness ('ITM', 'OTM', 'ATM')
    
    Returns:
        list: Filtered option positions
    """
    filtered_positions = []
    today = datetime.now()
    
    for position in positions:
        option_symbol = position.get('option_symbol', {})
        
        if not isinstance(option_symbol, dict):
            continue
        
        # Option type filter
        if option_type:
            position_type = option_symbol.get('option_type', '').upper()
            if position_type != option_type.upper():
                continue
        
        # Underlying symbol filter
        if underlying_symbol:
            underlying = option_symbol.get('underlying_symbol', {})
            if isinstance(underlying, dict):
                underlying_sym = underlying.get('symbol', '').upper()
                if underlying_sym != underlying_symbol.upper():
                    continue
        
        # Days to expiration filter
        if days_to_expiration:
            exp_date = option_symbol.get('expiration_date')
            if exp_date:
                try:
                    exp_date_obj = datetime.strptime(exp_date, '%Y-%m-%d')
                    days_to_exp = (exp_date_obj - today).days
                    if days_to_exp >= days_to_expiration:
                        continue
                except:
                    continue
        
        filtered_positions.append(position)
    
    return filtered_positions


# Example usage
def get_All_options_positions(user_id, user_secret):
    """Get all option positions for a user """

    all_options_positions_Data = {}
    call_options_positions = {}
    put_options_positions = {}
    expiring_soon_positions = {}
    # First get account list to get an account ID
    try:
        accounts_response = snaptradeconfig.account_information.list_user_accounts(
            user_id=user_id,
            user_secret=user_secret
        )
        accounts_Data = accounts_response.body
        
        for accounts in accounts_Data:
            temp_call = {}
            temp_put = {}
            temp_expiring_soon = {}
            first_account_id = accounts.get('id')
            first_account_name = accounts.get('name', 'First Account')
            all_options_positions_Data['Account_name'] = first_account_name
            if first_account_id:
                # Get option positions
                print(f"Fetching option positions for account: {first_account_name} (ID: {first_account_id})")
                option_positions = get_user_account_option_positions(user_id, user_secret, first_account_id)
                
                
                if option_positions:
                    # Example filtering
                    print(f"\nFiltering examples:")
                    call_options = filter_option_positions_by_criteria(option_positions, option_type='CALL')
                    temp_call['call_options'] = call_options
                    
                    put_options = filter_option_positions_by_criteria(option_positions, option_type='PUT')
                    temp_put['put_options'] = put_options
                    
                    expiring_soon = filter_option_positions_by_criteria(option_positions, days_to_expiration=30)
                    temp_expiring_soon['expiring_soon'] = expiring_soon
                    
                
                else:
                    
                    print("No option positions found in this account.")
            
            else:
                print("No account ID found.")
            
            
            if len(temp_call) > 0:
                call_options_positions[first_account_name] = temp_call    
            if len(temp_put) > 0:
                put_options_positions[first_account_name] = temp_put
            if len(temp_expiring_soon) > 0:
                expiring_soon_positions[first_account_name] = temp_expiring_soon
            
        if len(call_options_positions) > 0:
            all_options_positions_Data['call_options'] = call_options_positions
        if len(put_options_positions) > 0:
            all_options_positions_Data['put_options'] = put_options_positions
        if len(expiring_soon_positions) > 0:
            all_options_positions_Data['expiring_soon'] = expiring_soon_positions
        
        if  len(call_options_positions) == 0 and len(put_options_positions) == 0 and len(expiring_soon_positions) == 0:
            all_options_positions_Data['positions'] = "No option positions found."
            all_options_positions_Data['call_options'] = "0"
            all_options_positions_Data['put_options'] = "0"
            all_options_positions_Data['expiring_soon'] = "0"
            all_options_positions_Data['Total Options positions'] = len(call_options_positions) + len(put_options_positions) + len(expiring_soon_positions)
        
        return all_options_positions_Data
            
            
    except Exception as e:
        all_options_positions_Data['positions'] = "Error in fetching option positions. error: " + str(e)
        return all_options_positions_Data
