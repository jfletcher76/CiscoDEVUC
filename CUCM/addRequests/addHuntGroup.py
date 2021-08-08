# This script will create all you need for a hunt group and tie it all together
# This creates a Line Group, Hunt List, and Pilot
# There's also logic to specify if you want calls to rona to a VM box
# If you want calls to rona to another number other than a VM box you will need to tweak the code a bit

from lxml import etree
from requests import Session
from requests.auth import HTTPBasicAuth
from zeep import Client, Settings, Plugin, xsd
from zeep.transports import Transport
from zeep.exceptions import Fault
import sys
import urllib3
import random

# Edit .env file to specify your Webex site/user details
import os
from dotenv import load_dotenv
load_dotenv()

# Change to true to enable output of request/response headers and XML
DEBUG = False

# The WSDL is a local file in the working directory, see README
# WSDL_FILE = 'schema/AXLAPI.wsdl'
WSDL_FILE = '<your wsdl file path here>'

# This class lets you view the incoming and outgoing http headers and XML

class MyLoggingPlugin( Plugin ):

    def egress( self, envelope, http_headers, operation, binding_options ):

        # Format the request body as pretty printed XML
        xml = etree.tostring( envelope, pretty_print = True, encoding = 'unicode')

        print( f'\nRequest\n-------\nHeaders:\n{http_headers}\n\nBody:\n{xml}' )

    def ingress( self, envelope, http_headers, operation ):

        # Format the response body as pretty printed XML
        xml = etree.tostring( envelope, pretty_print = True, encoding = 'unicode')

        print( f'\nResponse\n-------\nHeaders:\n{http_headers}\n\nBody:\n{xml}' )

# The first step is to create a SOAP client session
session = Session()

# We avoid certificate verification by default
# And disable insecure request warnings to keep the output clear
session.verify = False
urllib3.disable_warnings( urllib3.exceptions.InsecureRequestWarning )

# To enabled SSL cert checking (recommended for production)
# place the CUCM Tomcat cert .pem file in the root of the project
# and uncomment the line below

# session.verify = 'changeme.pem'

# Add Basic Auth credentials
session.auth = HTTPBasicAuth( os.getenv( 'AXL_USERNAME' ), os.getenv( 'AXL_PASSWORD' ) )

# Create a Zeep transport and set a reasonable timeout value
transport = Transport( session = session, timeout = 10 )

# strict=False is not always necessary, but it allows zeep to parse imperfect XML
settings = Settings( strict = False, xml_huge_tree = True )

# If debug output is requested, add the MyLoggingPlugin callback
plugin = [ MyLoggingPlugin() ] if DEBUG else [ ]

# Create the Zeep client with the specified settings
client = Client( WSDL_FILE, settings = settings, transport = transport,
        plugins = plugin )

# Create the Zeep service binding to AXL at the specified CUCM
service = client.create_service( '{http://www.cisco.com/AXLAPIService/}AXLAPIBinding',
                                f'https://{os.getenv( "CUCM_ADDRESS" )}:8443/axl/' )

print('')
print('Add Hunt Group Script')
print('')
siteCode=input('Enter 4 Digit Site Code: ') # you can change siteCode to what you want, like huntGroupName maybe
locationType=input('Enter Location Type: ') # optional, you can remove this and just use site sideCode
globalName=(f'{siteCode}_{locationType}')
print('')
print('Department name would be like Front_Office or Cash_Room')
print('DO NOT include any spaces in name')
print('')
deptName=input('Enter Dept Name: ')
print('')
extension=input('Enter Pilot Extension: ')
print('')
# You need to have a RONA location.  We can't let calls ring forever
ronaToNumber=input('Enter where calls RONA to: ')
print('')

# Checks to see if RONA is a voicemail so it knows to set the *
isVM=input('Is RONA number a Unity VM box? (Y/N): ')
choice=False
while choice == False:
    isVM=input('Yes or No: ')
    if isVM.upper() == 'Y':
        ronaTo=( '*' + ronaToNumber )
        mask=( ronaToNumber )
        choice=True
    elif isVM.upper() == 'N':
        ronaTo=( ronaToNumber )
        mask=('')
        choice=True
    else:
        print('Invalid selection, please try again.')

# This will do its best to pick a CM Group to help maintain balance between active subscribers
# if you only have 1 active subscriber with 1 backup, you can remove this code and just specify your CM group in the 
# hunt list creation part by putting cucmGroup=('<your cucm group'>) above with the user input variables 
# Optional Begin
rando=random.randint(1,1000)
iRemainder = (rando % 2)
if iRemainder == 0:
    cucmGroup = '<enter your CM group here>'
else:
    cucmGroup = '<enter your CM group here>'
# Optional End

# Create Line Group
lineGroup = {
    'name': ( f'{globalName}_{deptName}_LG' ),
    'distributionAlgorithm': 'Broadcast',
    'rnaReversionTimeOut': '32',
    'huntAlgorithmNoAnswer': 'Try next member; then, try next group in Hunt List',
    'huntAlgorithmBusy': 'Try next member; then, try next group in Hunt List',
    'huntAlgorithmNotAvailable': 'Try next member; then, try next group in Hunt List'
}

# Execute the addLineGroup request
try:
    resp = service.addLineGroup( lineGroup )

except Fault as err:
    print( f'Zeep error: addLineGroup: { err }' )
    sys.exit( 1 )

print( '\naddLineGroup response:\n' )
print( resp,'\n' )

# Create Hunt List
huntList = {
    'name': ( f'{globalName}_{deptName}_HL' ),
    'description': ( f'{globalName}_{deptName}_HL'),
    'callManagerGroupName': (cucmGroup),
    'routeListEnabled': 'true',
    'voiceMailUsage': 'true',
    'members':
        {
        'member':
            {
            'lineGroupName': ( f'{globalName}_{deptName}_LG' ),
            'selectionOrder': "1"
            }
        }
}

# Execute the addHuntList request
try:
    resp = service.addHuntList( huntList )

except Fault as err:
    print( f'Zeep error: addHuntList: { err }' )
    sys.exit( 1 )

print( '\naddHuntList response:\n' )
print( resp,'\n' )

# Create Pilot Number
huntPilot = {
    'pattern': (extension),
    'description': ( f'{globalName}_{deptName}_Pilot' ),
    'routePartitionName': ('<your partition here>'),
    'patternUrgency': 'false',
    'patternPrecedence': '',    
    'provideOutsideDialtone': 'false',
    'huntListName': ( f'{globalName}_{deptName}_HL' ),
    'alertingName': ( '""' + globalName + '_' + deptName + '""'), # need "" quotes because in CUCM 12.5x hunt group name doesn't pass to clients phones
    'asciiAlertingName': ( f'{globalName}_{deptName}' ),
    'maxHuntduration': '32',
    'blockEnable': 'false',
    'useCallingPartyPhoneMask': '',
# if site needs to route calls that are busy or no answer to another destination, need to include the following and set destination
    'forwardHuntNoAnswer':
        {
        'usePersonalPreferences': 'false',
        'destination': ( ronaTo ),
        'callingSearchSpaceName': ( '<your calling search space here>' )
        },
    'forwardHuntBusy':
        {
        'usePersonalPreferences': 'false',
        'destination': ( ronaTo ),
        'callingSearchSpaceName': ( '<your calling search space here>' )
        },
    'calledPartyTransformationMask': ( mask )

# if site is sending calls to VM that does NOT = pilot number then you need to include the following and enter the VM Extension 
#    'calledPartyTransformationMask': (ronaTo)
}

# Execute the addHuntPilot request
try:
    resp = service.addHuntPilot( huntPilot )

except Fault as err:
    print( f'Zeep error: addHuntPilot: { err }' )
    sys.exit( 1 )

print( '\naddHuntPilot response:\n' )
print( resp,'\n' )