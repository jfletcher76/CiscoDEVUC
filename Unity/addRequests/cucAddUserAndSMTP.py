# This script will add a user and add smtp info to the notification devices as well
# You may want to modify things like Alias and DisplayName to fit your environment
# Make sure you point the first post to your appropriate VM template

import requests
from requests.auth import HTTPBasicAuth
import logging
from http.client import HTTPConnection
import os
import sys
import urllib3
import json
# loads .env file for authentication information
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
userEmail=(firstName + '.' + lastName + '@' + userDomain)
phoneExt=input('Enter user extension: ')

# Create a new user
req = {
    'Alias': (userEmail), # Modify this to fit whatever alias format you are using, we use first.last@email.com as you can see above
    'FirstName': (firstName),
    'LastName': (lastName),
    'DtmfAccessId': (phoneExt),
    'EmailAddress': (userEmail),
    'DisplayName': (lastName + ', ' + firstName)
}

try:
    resp = requests.post( 
        f'https://{ os.getenv( "CUC_ADDRESS" ) }/vmrest/users?templateAlias=User_Template_Here', # change "user_template_here to your VM template you want to use
        auth=HTTPBasicAuth( os.getenv( 'CUC_USER' ), os.getenv( 'CUC_PASSWORD' ) ),
        json = req,
        verify = False
        )

    # Raise an exception if a non-200/201 HTTP response received
    resp.raise_for_status()
    
    print('')
    print('Account Successfully Created: ', resp)
    
except Exception as err:
    print('')
    print( f'Request error: POST ../users: { err }' )
    print('')
    print('Account Creation Error: ', resp)
    print('')
    sys.exit

#Send Request to get URI

resp = requests.get( 
    f'https://{ os.getenv( "CUC_ADDRESS" ) }/vmrest/users?query=(EmailAddress is {userEmail})',
    auth = HTTPBasicAuth( os.getenv( 'CUC_USER' ), os.getenv( 'CUC_PASSWORD' ) ),
    headers = { 'Accept' : 'application/json' },
    verify = False
    )

# Load json data for variable assignment
json_data = json.loads(resp._content)
notifyDevices = json_data['User']['NotificationDevicesURI']
#notifyDevices = resp.json()['User']['NotificationDevicesURI']

#Send request to get SMTP devices
resp = requests.get( 
    f'https://{ os.getenv( "CUC_ADDRESS" ) }{notifyDevices}/smtpdevices',
    auth = HTTPBasicAuth( os.getenv( 'CUC_USER' ), os.getenv( 'CUC_PASSWORD' ) ),
    headers = { 'Accept' : 'application/json' },
    verify = False
    )

# Load json data for variable assignment
json_data = json.loads(resp._content)
uri = json_data['SmtpDevice']['URI']

#Update user SMTP
req = {
    'SmtpAddress': (userEmail),
    'Active': 'true',
    'PhoneNumber': 'UnityVMNotifications'
}

try:
    resp = requests.put( 
        f'https://{ os.getenv( "CUC_ADDRESS" ) }{uri}',
        auth=HTTPBasicAuth( os.getenv( 'CUC_USER' ), os.getenv( 'CUC_PASSWORD' ) ),
        json = req,
        verify = False
        )

    # Raise an exception if a non-200/201 HTTP response received
    resp.raise_for_status()
    
    print('SMTP Notifications Successfully Updated: ', resp)
        
except Exception as err:
    print('')
    print( f'Request error: PUT ../users: { err }' )
    print('')
    print('Account Creation Error: ', resp)
    print('')
    sys.exit