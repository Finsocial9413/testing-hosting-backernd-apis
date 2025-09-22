import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(os.path.abspath(__file__))))))

from common_import import *
# listing all users
def market_order(user_id, user_secret,account_id,symbol, unit,time_in_force):
    response = snaptradeconfig.trading.place_force_order(
        user_id=user_id,
        user_secret=user_secret,
        account_id=account_id,
        action= "BUY",
        symbol=symbol,
        order_type= "Market",
        time_in_force= time_in_force,
        units= int(unit),
    )
    return response.body  # Add this line to return the response data
