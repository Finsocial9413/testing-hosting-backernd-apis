
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(os.path.abspath(__file__))))))

from common_import import *

def get_specific_broker_details(user_id, user_secret,institution_name):
    """ List all accounts for a user    """
    response = snaptradeconfig.account_information.list_user_accounts(
        user_id=user_id,
        user_secret=user_secret     
    )
    broker_details = {}
    for i in range(len(response.body)):
        if institution_name in response.body[i]['name']:
            account_name = response.body[i]['name']
            broker_details['Account Name'] = account_name
            broker_details['brokerage_authorization'] = response.body[i]['brokerage_authorization']
            break
    

    return broker_details


# list_user_accounts("123", "0340489a-b8cd-4738-88a5-d88c2ecc62de", "Alpaca Paper")