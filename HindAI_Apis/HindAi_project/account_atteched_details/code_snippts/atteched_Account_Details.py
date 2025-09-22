import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common_import import *

def get_user_account_details(user_id, user_secret, account_id):
    """
    Get detailed information about a specific account
    
    Args:
        user_id (str): User ID for the SnapTrade user
        user_secret (str): User secret for the SnapTrade user
        account_id (str): Account ID to get details for
    
    Returns:
        dict: Account details including balances, positions, and metadata
    """
    
    try:
        response = snaptradeconfig.account_information.get_user_account_details(
            user_id=user_id,
            user_secret=user_secret,
            account_id=account_id
        )
        return response.body
    except Exception as e:
        print(f"Error getting account details for {account_id}: {e}")
        return None

def display_account_details(account_details):
    """
    Display account details in a formatted way
    
    Args:
        account_details (dict): Account details object
    """
    if not account_details:
        print("No account details available.")
        return
    
    print("\nAccount Details:")
    print("=" * 60)
    
    # Basic account information
    print(f"Account ID: {account_details.get('id', 'N/A')}")
    print(f"Account Name: {account_details.get('name', 'N/A')}")
    print(f"Account Number: {account_details.get('number', 'N/A')}")
    print(f"Account Type: {account_details.get('type', 'N/A')}")
    print(f"Institution Name: {account_details.get('institution_name', 'N/A')}")
    print(f"Status: {account_details.get('status', 'N/A')}")
    
    # Account balances
    if 'balance' in account_details:
        balance = account_details['balance']
        print(f"\nAccount Balance:")
        
        # Handle different balance formats
        if isinstance(balance, dict):
            # Check if balance has amount and currency fields
            if 'amount' in balance and 'currency' in balance:
                print(f"  Total: ${balance.get('amount', 'N/A')} {balance.get('currency', 'USD')}")
            else:
                print(f"  Total: ${balance.get('total', 'N/A')}")
            
            print(f"  Cash: ${balance.get('cash', 'N/A')}")
            print(f"  Equity: ${balance.get('equity', 'N/A')}")
            print(f"  Currency: {balance.get('currency', 'N/A')}")
        else:
            print(f"  Total: {balance}")
    
    # Account meta information
    if 'meta' in account_details:
        meta = account_details['meta']
        print(f"\nAccount Metadata:")
        if isinstance(meta, dict):
            for key, value in meta.items():
                print(f"  {key}: {value}")
        else:
            print(f"  {meta}")
    
    # Created date
    if 'created_date' in account_details:
        print(f"\nCreated Date: {account_details['created_date']}")
    
    # Brokerage information
    if 'brokerage_authorization' in account_details:
        auth = account_details['brokerage_authorization']
        print(f"\nBrokerage Authorization:")
        
        # Handle different brokerage_authorization formats
        if isinstance(auth, dict):
            print(f"  ID: {auth.get('id', 'N/A')}")
            print(f"  Name: {auth.get('name', 'N/A')}")
            print(f"  Type: {auth.get('type', 'N/A')}")
            
            if 'brokerage' in auth:
                brokerage = auth['brokerage']
                if isinstance(brokerage, dict):
                    print(f"  Brokerage Name: {brokerage.get('name', 'N/A')}")
                    print(f"  Brokerage Slug: {brokerage.get('slug', 'N/A')}")
                else:
                    print(f"  Brokerage: {brokerage}")
        else:
            print(f"  {auth}")
    
    print("-" * 60)

def get_all_accounts_details(user_id, user_secret):
    """
    Get detailed information for all accounts belonging to a user
    
    Args:
        user_id (str): User ID for the SnapTrade user
        user_secret (str): User secret for the SnapTrade user
    
    Returns:
        list: List of account details
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
        
        # Get detailed information for each account
        all_account_details = []
        for account in accounts:
            account_id = account.get('id')
            if account_id:
                details = get_user_account_details(user_id, user_secret, account_id)
                if details:
                    all_account_details.append(details)
        
        return all_account_details
        
    except Exception as e:
        print(f"Error getting all account details: {e}")
        return []


def compare_accounts(accounts_details):
    """
    Compare and analyze multiple accounts
    
    Args:
        accounts_details (list): List of account details
    
    Returns:
        dict: Comparison statistics
    """
    if not accounts_details:
        return {}
    
    stats = {
        'total_accounts': len(accounts_details),
        'account_types': {},
        'brokerages': {},
        'currencies': {},
        'total_value': 0,
        'largest_account': None,
        'smallest_account': None
    }
    
    account_values = []
    
    for account in accounts_details:
        # Count account types
        account_type = account.get('type', 'Unknown')
        stats['account_types'][account_type] = stats['account_types'].get(account_type, 0) + 1
        
        # Count brokerages - handle string brokerage_authorization
        if 'brokerage_authorization' in account:
            brokerage_auth = account['brokerage_authorization']
            if isinstance(brokerage_auth, dict):
                brokerage_name = brokerage_auth.get('brokerage', {}).get('name', 'Unknown')
            else:
                # If it's a string, use it as the brokerage name or use institution name
                brokerage_name = account.get('institution_name', 'Unknown')
            stats['brokerages'][brokerage_name] = stats['brokerages'].get(brokerage_name, 0) + 1
        
        # Count currencies and calculate totals
        if 'balance' in account:
            balance = account['balance']
            if isinstance(balance, dict):
                currency = balance.get('currency', 'USD')
                stats['currencies'][currency] = stats['currencies'].get(currency, 0) + 1
                
                # Handle different balance formats
                balance_amount = 0
                if 'amount' in balance:
                    balance_amount = balance.get('amount', 0)
                elif 'total' in balance:
                    balance_amount = balance.get('total', 0)
                
                try:
                    balance_float = float(balance_amount)
                    stats['total_value'] += balance_float
                    account_values.append((account, balance_float))
                except (ValueError, TypeError):
                    pass
    
    # Find largest and smallest accounts
    if account_values:
        account_values.sort(key=lambda x: x[1], reverse=True)
        stats['largest_account'] = account_values[0][0]
        stats['smallest_account'] = account_values[-1][0]
    
    return stats


# Example usage
def available_attached_account_details(user_id, user_secret):

    print("SnapTrade Account Details Tool")
    print("=" * 60)
    
    # Get all account details
    print("Fetching all account details...")
    all_accounts = get_all_accounts_details(user_id, user_secret)
    
    if all_accounts:
        # Display detailed information for each account
        for account in all_accounts:
            display_account_details(account)
        
        # Display summary
        
        # Display comparison and analysis
        stats = compare_accounts(all_accounts)
        
        # Raw data for debugging
        print(f"\n{'='*60}")
        print("RAW ACCOUNT DETAILS DATA:")
        pprint(all_accounts)
    else:
        print("No accounts found or failed to retrieve account details.")
    
    # Example: Get details for a specific account
    print(f"\n{'='*60}")
    print("Example: Getting details for a specific account...")
    
    # First get account list to get an account ID
    try:
        accounts_response = snaptradeconfig.account_information.list_user_accounts(
            user_id=user_id,
            user_secret=user_secret
        )
        accounts = accounts_response.body
        
        if accounts:
            first_account_id = accounts[0].get('id')
            if first_account_id:
                print(f"Getting details for account ID: {first_account_id}")
                account_details = get_user_account_details(user_id, user_secret, first_account_id)
                if account_details:
                    display_account_details(account_details)
                else:
                    print("Failed to get account details.")
            else:
                print("No account ID found.")
        else:
            print("No accounts found.")
    except Exception as e:
        print(f"Error in example: {e}")