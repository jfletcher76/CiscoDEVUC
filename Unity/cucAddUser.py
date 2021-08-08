# This script will add a user to Unity.  You will need to know your tempaltes 
# to include in the script below

# This script assumes your alias is the email address of the person.  If not you need to modify the script 

import requests
from requests.auth import HTTPBasicAuth
import logging
from http.client import HTTPConnection
import os
import sys
import urllib3
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
firstName=input('Enter First Name: ')
lastName=input('Enter Last Name: ')
userDomain=input('Enter domain without @: ')
userAlias=(firstName + '.' + lastName + '@' + userDomain) # <-- If your user Ids are not email based, change this line
userExt=input('Enter user extension: ')
vmTemplateQ=input('Enter is this an Anon vm box? (Y/N): ') # <-- I use different tempaltes for owned and non-owned VMs.  Include your templates here

if vmTemplateQ.upper() == 'Y':
    vmTemplate='<user template without office 365 integration>'
else:
    vmTemplate='voicemailusertemplate'

# Create a new user
req = {
    'Alias': (userAlias),
    'FirstName': (firstName),
    'LastName': (lastName),
    'DtmfAccessId': (userExt),
    'EmailAddress': (userAlias),
    'DisplayName': (lastName + ', ' + firstName)
}

try:
    resp = requests.post( 
        f'https://{ os.getenv( "CUC_ADDRESS" ) }/vmrest/users?templateAlias=' + vmTemplate,
        auth=HTTPBasicAuth( os.getenv( 'CUC_USER' ), os.getenv( 'CUC_PASSWORD' ) ),
        json = req,
        verify = False
        )

    # Raise an exception if a non-200/201 HTTP response received
    resp.raise_for_status()
    
    print('')
    print('Account Successfully Created: ', resp)
    print('')
    
except Exception as err:
    print('')
    print( f'Request error: POST ../users: { err }' )
    print('')
    print('Account Creation Error: ', resp)
    print('')
    sys.exit( 1 )
