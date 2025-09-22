
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(os.path.abspath(__file__))))))

from common_import import *

def get_account_holdings(user_id, user_secret, account_id):
    """
    Get holdings for a specific account
    
    Args:
        user_id (str): User ID for the SnapTrade user
        user_secret (str): User secret for the SnapTrade user
        account_id (str): Account ID to get holdings for
    
    Returns:
        list: List of holding objects for the account
    """
    
    try:
        response = snaptradeconfig.account_information.get_user_holdings(
            user_id=user_id,
            user_secret=user_secret,
            account_id=account_id
        )
        
        
        # Handle different response structures
        if isinstance(response.body, dict):
            # If it's a dict, look for positions or holdings
            if 'positions' in response.body:
                return response.body['positions']
            elif 'holdings' in response.body:
                return response.body['holdings']
            else:
                # Return the whole dict if it contains holding data
                return [response.body]
        elif isinstance(response.body, list):
            # If it's already a list, return it
            return response.body
        else:
            print(f"Unexpected response type: {type(response.body)}")
            return []
            
    except Exception as e:
        print(f"Error getting holdings for account {account_id}: {e}")
        return None

def list_user_accounts_holdings(user_id, user_secret):
    """
    Get all holdings across all accounts for a user
    
    Args:
        user_id (str): User ID for the SnapTrade user
        user_secret (str): User secret for the SnapTrade user
    
    Returns:
        list: List of holding objects across all accounts
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
            return []
        
        # Get holdings for each account
        all_holdings = []
        for account in accounts:
            account_id = account.get('id')
            if account_id:
                holdings = get_account_holdings(user_id, user_secret, account_id)
                if holdings:
                    all_holdings.extend(holdings)
        
        return all_holdings
        
    except Exception as e:
        print(f"Error getting user holdings: {e}")
        return None

def display_holdings_details(holdings):
    """Display detailed information about holdings"""
    if not holdings:
        print("No holdings found.")
        return
    
    # Debug: Check what type of data we're receiving
    print(f"DEBUG: Holdings type: {type(holdings)}")
    if holdings:
        print(f"DEBUG: First holding type: {type(holdings[0])}")
        print(f"DEBUG: First holding content: {holdings[0]}")
    
    for i, holding in enumerate(holdings, 1):
        print(f"\nHolding {i}:")
        print("=" * 100)
        
        # Check if holding is a string or dict
        if isinstance(holding, str):
            print(f"  Raw data: {holding}")
            continue
        elif not isinstance(holding, dict):
            print(f"  Unexpected data type: {type(holding)}")
            print(f"  Content: {holding}")
            continue
        
        # Handle symbol - it might be a string or dict
        symbol_info = holding.get('symbol', {})
        if isinstance(symbol_info, dict):
            symbol = symbol_info.get('symbol', 'N/A')
        else:
            symbol = symbol_info if symbol_info else 'N/A'
        
        print(f"  Symbol: {symbol}")
        
        # Handle other fields safely
        print(f"  Quantity: {holding.get('units', 'N/A')}")
        print(f"  Price: ${holding.get('price', 'N/A')}")
        print(f"  Market Value: ${holding.get('market_value', 'N/A')}")
        print(f"  Average Purchase Price: ${holding.get('average_purchase_price', 'N/A')}")
        
        # Handle currency
        currency_info = holding.get('currency', {})
        if isinstance(currency_info, dict):
            currency = currency_info.get('code', 'N/A')
        else:
            currency = currency_info if currency_info else 'N/A'
        print(f"  Currency: {currency}")
        
        # Handle exchange
        exchange_info = holding.get('exchange', {})
        if isinstance(exchange_info, dict):
            exchange = exchange_info.get('name', 'N/A')
        else:
            exchange = exchange_info if exchange_info else 'N/A'
        print(f"  Exchange: {exchange}")
        
        # Handle account
        account_info = holding.get('account', {})
        if isinstance(account_info, dict):
            account_name = account_info.get('name', 'N/A')
            account_number = account_info.get('number', 'N/A')
        else:
            account_name = 'N/A'
            account_number = 'N/A'
        print(f"  Account: {account_name} ({account_number})")
        
        print("-" * 100)

def get_holdings_summary(holdings):
    """
    Get summary statistics about user's holdings
    
    Args:
        holdings (list): List of holding objects
    
    Returns:
        dict: Summary statistics
    """
    if not holdings:
        return {
            "total_holdings": 0,
            "total_value": 0,
            "unique_symbols": 0,
            "symbols": [],
            "accounts": [],
            "total_pnl": 0,
            "currencies": []
        }
    
    total_holdings = len(holdings)
    total_value = 0
    total_pnl = 0
    symbols = set()
    accounts = set()
    currencies = set()
    
    for holding in holdings:
        # Calculate total value (quantity * price)
        try:
            units = float(holding.get('units', 0))
            price = float(holding.get('price', 0))
            total_value += units * price
        except (ValueError, TypeError):
            pass
        
        # Calculate total P&L
        try:
            pnl = float(holding.get('open_pnl', 0))
            total_pnl += pnl
        except (ValueError, TypeError):
            pass
        
        # Collect unique symbols
        symbol_info = holding.get('symbol', {})
        if symbol_info and 'symbol' in symbol_info:
            symbols.add(symbol_info['symbol'])
        
        # Collect unique accounts
        account_info = holding.get('account', {})
        if account_info and 'name' in account_info:
            accounts.add(account_info['name'])
        
        # Collect unique currencies
        if 'currency' in holding:
            currencies.add(holding['currency'])
    
    return {
        "total_holdings": total_holdings,
        "total_value": total_value,
        "unique_symbols": len(symbols),
        "symbols": list(symbols),
        "accounts": list(accounts),
        "total_pnl": total_pnl,
        "currencies": list(currencies)
    }

def filter_holdings(holdings, symbol=None, account_id=None, currency=None, min_value=None):
    """
    Filter holdings based on specific criteria
    
    Args:
        holdings (list): List of holding objects
        symbol (str, optional): Filter by symbol
        account_id (str, optional): Filter by account ID
        currency (str, optional): Filter by currency
        min_value (float, optional): Minimum holding value
    
    Returns:
        list: Filtered list of holdings
    """
    if not holdings:
        return []
    
    filtered = holdings
    
    if symbol:
        filtered = [
            holding for holding in filtered
            if holding.get('symbol', {}).get('symbol', '').upper() == symbol.upper()
        ]
    
    if account_id:
        filtered = [
            holding for holding in filtered
            if holding.get('account', {}).get('id', '') == account_id
        ]
    
    if currency:
        filtered = [
            holding for holding in filtered
            if holding.get('currency', '').upper() == currency.upper()
        ]
    
    if min_value:
        filtered_by_value = []
        for holding in filtered:
            try:
                units = float(holding.get('units', 0))
                price = float(holding.get('price', 0))
                value = units * price
                if value >= min_value:
                    filtered_by_value.append(holding)
            except (ValueError, TypeError):
                pass
        filtered = filtered_by_value
    
    return filtered

def display_holdings_by_account(holdings):
    """
    Display holdings grouped by account
    
    Args:
        holdings (list): List of holding objects
    """
    if not holdings:
        print("No holdings found.")
        return
    
    # Group holdings by account
    account_holdings = {}
    for holding in holdings:
        account_info = holding.get('account', {})
        account_name = account_info.get('name', 'Unknown Account')
        account_id = account_info.get('id', 'Unknown ID')
        account_key = f"{account_name} ({account_id})"
        
        if account_key not in account_holdings:
            account_holdings[account_key] = []
        account_holdings[account_key].append(holding)
    
    print(f"\nHoldings grouped by account:")
    print("=" * 90)
    
    for account_key, account_holdings_list in account_holdings.items():
        print(f"\n{account_key}:")
        print("-" * 50)
        
        account_total_value = 0
        account_total_pnl = 0
        
        for holding in account_holdings_list:
            symbol = holding.get('symbol', {}).get('symbol', 'N/A')
            name = holding.get('symbol', {}).get('name', 'N/A')
            units = holding.get('units', 0)
            price = holding.get('price', 0)
            pnl = holding.get('open_pnl', 0)
            
            try:
                value = float(units) * float(price)
                account_total_value += value
                account_total_pnl += float(pnl)
                
                print(f"  {symbol} - {name}")
                print(f"    Quantity: {units}, Price: ${price}, Value: ${value:.2f}, P&L: ${pnl}")
            except (ValueError, TypeError):
                print(f"  {symbol} - {name}")
                print(f"    Quantity: {units}, Price: ${price}, P&L: ${pnl}")
        
        print(f"\n  Account Total Value: ${account_total_value:.2f}")
        print(f"  Account Total P&L: ${account_total_pnl:.2f}")
        print("-" * 50)

def list_holdings_with_filters(user_id, user_secret, symbol=None, account_id=None, currency=None, min_value=None):
    """
    List user holdings with optional filtering
    
    Args:
        user_id (str): User ID for the SnapTrade user
        user_secret (str): User secret for the SnapTrade user
        symbol (str, optional): Filter by symbol
        account_id (str, optional): Filter by account ID
        currency (str, optional): Filter by currency
        min_value (float, optional): Minimum holding value
    
    Returns:
        list: Filtered list of holdings
    """
    
    print(f"Fetching holdings for user: {user_id}")
    if symbol:
        print(f"  Filtering by symbol: {symbol}")
    if account_id:
        print(f"  Filtering by account ID: {account_id}")
    if currency:
        print(f"  Filtering by currency: {currency}")
    if min_value:
        print(f"  Filtering by minimum value: ${min_value}")
    
    print("-" * 70)
    
    # Get all holdings
    all_holdings = list_user_accounts_holdings(user_id, user_secret)
    
    if all_holdings is None:
        print("Failed to retrieve holdings")
        return []
    
    # Apply filters
    filtered_holdings = filter_holdings(all_holdings, symbol, account_id, currency, min_value)
    
    if not filtered_holdings:
        print("No holdings match the specified criteria.")
        return []
    
    # Display results
    display_holdings_details(filtered_holdings)
    
    # Display grouped by account
    print(f"\n{'='*90}")
    display_holdings_by_account(filtered_holdings)
    
    # Display summary
    summary = get_holdings_summary(filtered_holdings)

    
    return filtered_holdings

# Example usage
def user_holdings_data(user_id, user_secret):
    """Example usage of the holdings functions"""

    holdings = list_holdings_with_filters(user_id, user_secret)
    
    if holdings:
        # Example: Filter by specific symbol
        print(f"\n{'='*90}")
        print("Example: Filtering by specific criteria:")
        
        # Get unique symbols for demonstration
        summary = get_holdings_summary(holdings)
        if summary['symbols']:
            first_symbol = summary['symbols'][0]
            print(f"\nHoldings for {first_symbol}:")
            symbol_holdings = list_holdings_with_filters(
                user_id, user_secret, 
                symbol=first_symbol
            )
        
        # Filter by minimum value
        print(f"\n{'='*90}")
        print("Holdings with value >= $100:")
        valuable_holdings = list_holdings_with_filters(
            user_id, user_secret
        )
        all_holdings = {}
        all_holdings['Holdings'] = holdings
        return all_holdings 
    else:
        all_holdings = {}
        all_holdings['Holdings'] = 'No holdings found for this user.'
        return all_holdings