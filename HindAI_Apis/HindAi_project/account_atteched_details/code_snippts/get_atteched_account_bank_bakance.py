import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common_import import *

def get_user_account_balance(account_id, user_id, user_secret):
    response = snaptradeconfig.account_information.get_user_account_balance(
        account_id=account_id,
        user_id=user_id,
        user_secret=user_secret
    )
    return response.body