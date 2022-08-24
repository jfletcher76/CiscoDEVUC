# This is an example of setting call recording and adding the line to a hunt group
# This will ask for an extension then it will setup the phone for call recording (if the phone is a CSF, if not you need to modify for SEP or others)
# Then it also will give you a list of part hunt groups and ask you to pick on that you need to add the extension to

# Variables to fix
# Find and replace yourPartition with the partition your phones use on their lines 

from requests import Session
from requests.auth import HTTPBasicAuth
from zeep import Client, Settings
from zeep.transports import Transport
from zeep.exceptions import Fault
import sys
import urllib3

# edit .env file for your server and credentials
import os
from dotenv import load_dotenv
load_dotenv()

DEBUG = False
# Add the path to your WSDL file on the line below
WSDL_FILE = 'AXLAPI.wsdl'
session = Session()
session.verify = False
urllib3.disable_warnings( urllib3.exceptions.InsecureRequestWarning )
session.auth = HTTPBasicAuth( os.getenv( 'AXL_USERNAME' ), os.getenv( 'AXL_PASSWORD' ) )
transport = Transport( session = session, timeout = 10 )
settings = Settings( strict = False, xml_huge_tree = True )
client = Client( WSDL_FILE, settings = settings, transport = transport)
service = client.create_service( '{http://www.cisco.com/AXLAPIService/}AXLAPIBinding',
                                f'https://{os.getenv( "CUCM_ADDRESS" )}:8443/axl/' )

deviceList=[]

# Enter extensions of the device you want to setup call recording for
print('')
phoneExt=input('Enter extension: ')

# run resp to get line info
try:
    resp = service.getLine(pattern = phoneExt, routePartitionName = 'yourPartition') 
except:
    print(f'\n{phoneExt} does not exist, exiting script\n')
    sys.exit

# Gets the devices associated to the line and also gets description of the line
deviceAssociation = resp["return"]["line"]["associatedDevices"]
lineDescription = resp["return"]["line"]["description"]

# Runs through the deviceAssociation list and pulls the CSF profile out, stops when it finds it
for x in deviceAssociation['device']:
    deviceList.append(x)
    if 'CSF' in x[:3]:
        csfProfile=x
        break

# Runs the update of the phone to add call recording
try:
    resp = service.updatePhone( 
        name = csfProfile, 
        builtInBridgeStatus = 'On',
        lines = {'line': {'index': '1', 'dirn': {'pattern': (phoneExt), 'routePartitionName': 'yourPartition'}, 'recordingMediaSource': 'Phone Preferred', 'recordingFlag': 'Automatic Call Recording Enabled', 'recordingProfileName': 'Call Recording Profile'}}
        )

    print(f'\nPhone {csfProfile} belonging to {lineDescription} updated. Moving on to adding to line group\n')

except Fault as err:
    print( f'Zeep error: updatePhone: { err }' )
    sys.exit

# Begin add user to line group

#Builds a list of DEPT line groups
#Change the DEPT to what you need to list your line groups
#If you are using a good naming standard, the first few letters should match a bunch of line groups you need to list
resp=service.listLineGroup(searchCriteria = {'name': 'DEPT%'}, returnedTags={'name': ''}) 
print(f'Please pick a line group to add {phoneExt} to')
print('-' * 20)
for x in resp['return']['lineGroup']:
    print(x['name'])
print('If you don\'t need a line group, enter 0 or hit enter')
print('-' * 20)
lineGroup=input('Choice: ')

# Checks first if the user needs a line group and if not, will skip adding line to a line group
if lineGroup != '0' and bool(lineGroup) == True:
    # Get number of members in LG if there are any and set lineSelect as the API needs to add the user in at the end of the list
    resp = service.getLineGroup(name = lineGroup)
    if resp['return']['lineGroup']['members'] is None:
        lineSelect = 1
    else:
        lgMembers=resp['return']['lineGroup']['members']['member']
        lineSelect=len(lgMembers) + 1

    # Update the line group with the extension 
    try:
        resp = service.updateLineGroup( name = lineGroup, addMembers = {'member': { 'lineSelectionOrder': lineSelect, 'directoryNumber': {'pattern': phoneExt, 'routePartitionName': 'yourPartition'} } } )
        print(f'\n{phoneExt} added to {lineGroup}\n')
    except:
        print(f'\nFailed to add {phoneExt} to {lineGroup}\n')
else:
    print(f'\n{phoneExt} for user {lineDescription} doesn\'t require a line group.\n')

print('Job Complete!\n')
