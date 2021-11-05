# This script just gets a list of templates and their URIs.
# You can change this script however you see fit if you need it to do something else within the getCallHandlerTemplate 

import requests
from requests.auth import HTTPBasicAuth
import logging
from http.client import HTTPConnection
import os
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

# Send Request

resp = requests.get( 
    f'https://{ os.getenv( "CUC_ADDRESS" ) }/vmrest/callhandlertemplates',
    auth = HTTPBasicAuth( os.getenv( 'CUC_USER' ), os.getenv( 'CUC_PASSWORD' ) ),
    headers = { 'Accept' : 'application/json' },
    verify = False
    )

# Load json data for print
json_data = json.loads(resp._content)
#json_formatted_str = json.dumps(json_data, indent=2)
#print(json_formatted_str)
print('')
for x in json_data['CallhandlerTemplate']:
    callHandlerTemplateName=x['DisplayName']
    callHandlerTempURI=x['URI']
    print(f'{callHandlerTemplateName}: URI - {callHandlerTempURI}')
print('')
