import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(os.path.abspath(__file__))))))

from common_import import *
# Registering a new user
def register_snaptrade_user(username):

    response = snaptradeconfig.authentication.register_snap_trade_user(
        user_id=username
    )
    return response

