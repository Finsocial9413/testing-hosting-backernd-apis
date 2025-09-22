
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(os.path.abspath(__file__))))))

from common_import import *

def get_all_broker_details(user_id, user_secret):
    """ List all accounts for a user    """
    response = snaptradeconfig.account_information.list_user_accounts(
        user_id=user_id,
        user_secret=user_secret     
    )

    broker_details = {}
    
    for i in range(len(response.body)):
        account_name = response.body[i]['name']
        temp = {
            "Account Name": account_name,
            "brokerage_authorization": response.body[i]['brokerage_authorization']
        }
        broker_details[account_name] = temp

    return broker_details


# list_user_accounts("123", "0340489a-b8cd-4738-88a5-d88c2ecc62de", "Alpaca Paper")