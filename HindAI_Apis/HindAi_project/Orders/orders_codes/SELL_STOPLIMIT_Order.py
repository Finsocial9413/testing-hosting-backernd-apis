import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(os.path.abspath(__file__))))))

from common_import import *



def SELL_stop_Order(user_id,user_secret,account_id,symbol,price,stop,units,time_in_force):
   
    response = snaptradeconfig.trading.place_force_order(
        user_id=user_id,
        user_secret=user_secret,
        account_id=account_id,
        action="SELL",
        symbol=symbol,
        order_type="StopLimit",
        time_in_force=time_in_force,
        price=price,
        stop=stop,
        units=units
    )
    return response.body
