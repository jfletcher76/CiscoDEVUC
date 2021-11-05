# This script gets the user info from the API so you can see the various things you might need in other scripts
# This script assumes you use email address for alias, if not you must modify script to use what you want

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

# Gather information 

print('')
userEmail=input('Enter user alias - first.last@domain.com: ') # <--- change this to what you want.  email, alias, extension, etc

# Send Request

resp = requests.get( 
    f'https://{ os.getenv( "CUC_ADDRESS" ) }/vmrest/users?query=(EmailAddress is {userEmail})', # <-- you can modify the (EmailAddress is {userEmail}) to what you want to search for.  Like extension or alias
    auth = HTTPBasicAuth( os.getenv( 'CUC_USER' ), os.getenv( 'CUC_PASSWORD' ) ),
    headers = { 'Accept' : 'application/json' },
    verify = False
    )
# to see raw content you can uncomment this next line
#print(resp._content)

# Load json data for print
json_data = json.loads(resp._content)
json_formatted_str = json.dumps(json_data, indent=2)
print(json_formatted_str)

