import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(os.path.abspath(__file__))))))

from common_import import *
# Deleting a Snaptrade user
def delete_snaptrade_user_data(username):
    response = snaptradeconfig.authentication.delete_snap_trade_user(
        user_id=username
    )
    return response

