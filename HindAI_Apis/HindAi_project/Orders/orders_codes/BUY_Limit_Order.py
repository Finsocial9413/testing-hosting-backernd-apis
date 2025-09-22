import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(os.path.abspath(__file__))))))

from common_import import *

def Buy_Limit_Order(user_id,user_secret,account_id,symbol,price,stop,units,time_in_force):
    response = snaptradeconfig.trading.place_force_order(
        user_id=user_id,
        user_secret=user_secret,
        account_id=account_id,
        action="BUY",
        symbol=symbol,
        order_type="Limit",
        time_in_force=time_in_force,
        price=price,
        stop=stop,
        units=units
    )
    return (response.body)