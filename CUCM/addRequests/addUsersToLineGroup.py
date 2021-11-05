# This script will add users to line groups you specify.
# It will ask you for users in a loop and build a list of users for you
# Then it will ask for the line group you want to modify and go add those users to the group

from requests import Session
from requests.auth import HTTPBasicAuth
from zeep import Client, Settings
from zeep.transports import Transport
import urllib3

# Edit .env file to specify your Webex site/user details
import os
from dotenv import load_dotenv
load_dotenv()

# Change to true to enable output of request/response headers and XML
DEBUG = False

# The WSDL is a local file in the working directory, see README
# WSDL_FILE = 'schema/AXLAPI.wsdl'
WSDL_FILE = '<path to your wsdl file here>'

# The first step is to create a SOAP client session
session = Session()

# We avoid certificate verification by default
# And disable insecure request warnings to keep the output clear
session.verify = False
urllib3.disable_warnings( urllib3.exceptions.InsecureRequestWarning )

# Add Basic Auth credentials
session.auth = HTTPBasicAuth( os.getenv( 'AXL_USERNAME' ), os.getenv( 'AXL_PASSWORD' ) )

# Create a Zeep transport and set a reasonable timeout value
transport = Transport( session = session, timeout = 10 )

# strict=False is not always necessary, but it allows zeep to parse imperfect XML
settings = Settings( strict = False, xml_huge_tree = True )

# Create the Zeep client with the specified settings
client = Client( WSDL_FILE, settings = settings, transport = transport)

# Create the Zeep service binding to AXL at the specified CUCM
service = client.create_service( '{http://www.cisco.com/AXLAPIService/}AXLAPIBinding',
                                f'https://{os.getenv( "CUCM_ADDRESS" )}:8443/axl/' )

# Begins the loop asking for your extensions and builds the userList 
loopChoice=False
userList = []
print('')
while loopChoice == False:
    userExt=input('Enter User Extension (enter 0 when complete): ')
    if len(userExt) != 11 and userExt != '0':
        print('')
        print('Invalid extension, try again')
    else:
        if userExt != '0':
            userList.append(userExt)
            print('')
        elif userExt == '0':
            loopChoice = True

# Asks for your line group in CUCM (case sensitive)
print('')
lineGroup=input('Enter line group to change: ')
print('')

# Get number of members in LG if there are any and set lineSelect
resp = service.getLineGroup(name = lineGroup)
if resp['return']['lineGroup']['members'] is None:
    lineSelect = 1
else:
    lgMembers=resp['return']['lineGroup']['members']['member']
    lineSelect=len(lgMembers) + 1

# Loops through userList and adds users to line group
for phoneExt in userList:
    try:
        # you will need to add your line partition in the following resp, at the end <add your partition here>
        resp = service.updateLineGroup( name = lineGroup, addMembers = {'member': { 'lineSelectionOrder': lineSelect, 'directoryNumber': {'pattern': phoneExt, 'routePartitionName': '<add your partition here>'} } } )
        print(f'{phoneExt} added to {lineGroup}.')
        lineSelect=lineSelect+1
    except:
        print(f'Could not add {phoneExt} to {lineGroup}, please investigate.')