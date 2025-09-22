import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(os.path.abspath(__file__))))))

from common_import import *

def cancel_order(account_id, user_id, user_secret, brokerage_order_id):
    try:
        print(f"Attempting to cancel order:")
        print(f"  account_id: {account_id}")
        print(f"  user_id: {user_id}")
        print(f"  user_secret: {user_secret}")
        print(f"  brokerage_order_id: {brokerage_order_id}")
        
        # Use the correct method for canceling orders
        response = snaptradeconfig.trading.cancel_user_account_order(
            account_id=account_id,
            user_id=user_id,
            user_secret=user_secret,
            brokerage_order_id=brokerage_order_id
        )
        
        print("Cancel order response received:")
        print(response.body)
        return response.body
        
    except Exception as e:
        print(f"Error in cancel_order function: {str(e)}")
        raise e
    
