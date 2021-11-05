# This script will add a call handler to the system based on name and extension you provide
# It will also ask you to pick a template from a list to apply to the call handler creation process

import requests
from requests.auth import HTTPBasicAuth
import logging
from http.client import HTTPConnection
import os
import sys
import urllib3
import json
# loads the .env file for authentication info
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

# Gather User Information for creation

print('')
callHandlerName=input('Enter Call Handler Name: ')
callHandlerExt=input('Enter Call Handler Ext: ')
print('')

# Gets the template URIs so you can pick the one you want to see
resp = requests.get( 
    f'https://{ os.getenv( "CUC_ADDRESS" ) }/vmrest/callhandlertemplates',
    auth = HTTPBasicAuth( os.getenv( 'CUC_USER' ), os.getenv( 'CUC_PASSWORD' ) ),
    headers = { 'Accept' : 'application/json' },
    verify = False
    )

# Load json data for variable assignment then displays the URIs and templates
json_data = json.loads(resp._content)
print('------------------------------------------------------------------------------')
for x in json_data['CallhandlerTemplate']:
    callHandlerTemplateName=x['DisplayName']
    callHandlerTempURI=x['URI']
    print(f'{callHandlerTemplateName}: URI {callHandlerTempURI}')
print('------------------------------------------------------------------------------')

print('')
callHandlerURI=input('Enter the URI you want to change from the list above: ')
print('')

# Create a new call handler
req = {
    'DisplayName': (callHandlerName),
    'DtmfAccessId': (callHandlerExt)
}

try:
    resp = requests.post( 
        f'https://{ os.getenv( "CUC_ADDRESS" ) }/vmrest/handlers/callhandlers?templateObjectId={callHandlerURI}',
        auth=HTTPBasicAuth( os.getenv( 'CUC_USER' ), os.getenv( 'CUC_PASSWORD' ) ),
        json = req,
        verify = False
        )

    # Raise an exception if a non-200/201 HTTP response received
    resp.raise_for_status()
    
    print('')
    print('Call Handler Successfully Created: ', resp)
    print('')
    
except Exception as err:
    print('')
    print( f'Request error: POST ../users: { err }' )
    print('')
    print('Call Handler Creation Error: ', resp)
    print('')
    sys.exit
