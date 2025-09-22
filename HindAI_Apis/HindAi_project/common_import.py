from pprint import pprint
from snaptrade_client import SnapTrade
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize SnapTrade client
snaptradeconfig = SnapTrade(
    client_id='FINSOCIAL-DIGITAL-SYSTEMS-HIKXK',
    consumer_key='dBTY4Y82cfghfyXVvXApFf6ToJMEDlXI1DI2oynzuvrAClLDdM'
)

# Define what gets imported when using "from common_import import *"
__all__ = [
    'pprint',
    'SnapTrade', 
    'os',
    'load_dotenv',
    'snaptradeconfig'
]
