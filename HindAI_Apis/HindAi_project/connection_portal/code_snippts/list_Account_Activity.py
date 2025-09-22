
import sys
import os
from datetime import datetime,timedelta
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(os.path.abspath(__file__))))))

from common_import import *



def list_of_Account_Activity(user_id, user_secret, account_id, start_date, end_date, offset=0, limit=1000, type=None):
    try:
        # List account activities
        get_account_activities_response_Data = {}
        if start_date is None:
            start_date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
            
        if end_date is None:
            end_date = (datetime.now()).strftime('%Y-%m-%d')
        get_account_activities_response = (
             snaptradeconfig.account_information.get_account_activities(
                account_id=account_id,
                user_id=user_id,
                user_secret=user_secret,
                start_date=start_date,
                end_date=end_date,
                offset=offset, #number of page to skip
                limit=limit,  #number of activities to return mx return 1000
                type="BUY,SELL,DIVIDEND",
            )
        )
        get_account_activities_response_Data['account_activities'] = get_account_activities_response.body
        return get_account_activities_response_Data
    except Exception as e:
        get_account_activities_response_Data['error'] = (
            "Exception when calling AccountInformationApi.get_account_activities: %s\n"
            % e
        )
        return get_account_activities_response_Data

