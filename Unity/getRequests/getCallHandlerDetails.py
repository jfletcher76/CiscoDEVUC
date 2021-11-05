# This script will give you the details of a call handler you enter the name of

import requests
from requests.auth import HTTPBasicAuth
import logging
from http.client import HTTPConnection
import os
import sys
import urllib3
import json
from dotenv import load_dotenv
load_dotenv()

# Disable insecure request warnings to keep the output clear
urllib3.disable_warnings( urllib3.exceptions.InsecureRequestWarning )

# Change to true to enable request/response debug output
DEBUG = False

if DEBUG:
    print()
    log = logging.getLogger( 'urllib3' )
    log.setLevel( logging.DEBUG )

    # logging from urllib3 to console
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    log.addHandler( ch )

    # print statements from `http.client.HTTPConnection` to console/stdout
    HTTPConnection.debuglevel = 1

# Get call handler name
print('')
callHandlerName=input('Enter call handler name: ')
print('')

# Send Request
resp = requests.get( 
    f'https://{ os.getenv( "CUC_ADDRESS" ) }/vmrest/handlers/callhandlers?query=(DisplayName is {callHandlerName})',
    auth = HTTPBasicAuth( os.getenv( 'CUC_USER' ), os.getenv( 'CUC_PASSWORD' ) ),
    headers = { 'Accept' : 'application/json' },
    verify = False
    )

# Load json data for print

json_data = json.loads(resp._content)
json_formatted_str = json.dumps(json_data, indent=2)
print(json_formatted_str)