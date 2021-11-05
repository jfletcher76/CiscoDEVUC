# This script will reset the PIN of the user you specify
# It will also unlock the account and set the flag for change at next login

import requests
from requests.auth import HTTPBasicAuth
import logging
from http.client import HTTPConnection
import os
import sys
import urllib3
import json
# Loads .env file with user authentication info
from dotenv import load_dotenv
load_dotenv()
# Imports the modfule for the menu, you will need to install this modfule if you don't have it
# or modify the script to remove this menu and just do text input prompts
import PySimpleGUI as sg

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
layout = [
    [sg.Text('Please enter the below info')],
    [sg.Text('Enter extension number of user you want to change, and the PIN you want to change to')],
    [sg.HorizontalSeparator()],
    [sg.Text('Extension: ', size =(14, 1)), sg.InputText()],
    [sg.Text('PIN: ', size =(14, 1)), sg.InputText()],
    [sg.Text('')],
    [sg.Submit(), sg.Cancel()]
]
  
window = sg.Window('Change Unity VM PIN', layout)
while True:
    event, values = window.read()
    if event=="Cancel" or event==sg.WIN_CLOSED:
        break
    elif event=='Submit':
        userExt=values[1]
        pinCode=values[2]
        window.close()

# Get the user object ID for the update
resp = requests.get( 
    f'https://{ os.getenv( "CUC_ADDRESS" ) }/vmrest/users?query=(DtmfAccessId is {userExt})',
    auth = HTTPBasicAuth( os.getenv( 'CUC_USER' ), os.getenv( 'CUC_PASSWORD' ) ),
    headers = { 'Accept' : 'application/json' },
    verify = False
    )

json_data = json.loads(resp._content)
userID = json_data['User']['ObjectId']

# Update user PIN
req = {
    'Credentials': (pinCode),
    'CredMustChange': 'true',
    'HackCount': '0'
}

try:
    resp = requests.put( 
        f'https://{ os.getenv( "CUC_ADDRESS" ) }/vmrest/users/{userID}/credential/pin',
        auth=HTTPBasicAuth( os.getenv( 'CUC_USER' ), os.getenv( 'CUC_PASSWORD' ) ),
        json = req,
        verify = False
        )

    # Raise an exception if a non-200/201 HTTP response received
    resp.raise_for_status()
    
    print('')
    print('PIN Successfully changed: ', resp)
    print('')

except Exception as err:
    print('')
    print( f'Request error: POST ../users: { err }' )
    print('')
    print('Account Change Error: ', resp)
    print('')
    sys.exit( 1 )