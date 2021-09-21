# This script will add a line and a client services framework device (jabber)

from lxml import etree
from requests import Session
from requests.auth import HTTPBasicAuth
from zeep import Client, Settings, Plugin, xsd
from zeep.transports import Transport
from zeep.exceptions import Fault
import sys
import urllib3

# Edit .env file to specify your Webex site/user details
import os
from dotenv import load_dotenv
load_dotenv()

# Change to true to enable output of request/response headers and XML
DEBUG = False

# The WSDL is a local file in the working directory, see README
# WSDL_FILE = 'schema/AXLAPI.wsdl'
WSDL_FILE = '<your wsdl path here>'

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

# User input here.  This script assumes you use email address as user ID in CUCM.
# If you use another type of username, you will need to modify the script
phoneExt=input('Enter a Directory Number: ')
partition=input('Enter Null Parition Name: ')
siteCode=input('Enter site code: ')
locationType=input('Enter locaiton type: ')
globalName=(f'{siteCode}_{locationType}')
firstName=input('Enter First Name: ')
lastName=input('Enter Last Name: ')
userDomain=('Enter user domain (do not include @, just domain.com): ')
userEmail=(f'{firstName}.{lastName}@{userDomain}')

# Create a test Line
line = {
    'pattern': (phoneExt),
    'description': (lastName + ', ' + firstName),
    'alertingName': (lastName + ', ' + firstName),
    'asciiAlertingName': (lastName + ', ' + firstName),
    'usage': 'Device',
    'routePartitionName': ('<your partition here>'),
    'voiceMailProfileName': '<your VM profile here>',
    'shareLineAppearanceCssName': ('<your css here>'),
    'callForwardAll':
        {
        'forwardToVoiceMail': 'False',
        'callingSearchSpaceName': ('<your css here>'),
        'secondaryCallingSearchSpaceName': ('<your css here>')
        },
    'callForwardBusy':
        {
        'forwardToVoiceMail': 'True',
        'callingSearchSpaceName': ('<your css here>')
        },
    'callForwardBusyInt':
        {
        'forwardToVoiceMail': 'True',
        'callingSearchSpaceName': ('<your css here>')
        },
    'callForwardNoAnswer':
        {
        'forwardToVoiceMail': 'True',
        'callingSearchSpaceName': ('<your css here>')
        },
    'callForwardNoAnswerInt':
        {
        'forwardToVoiceMail': 'True',
        'callingSearchSpaceName': ('<your css here>')
        },
    'callForwardNoCoverage':
        {
        'forwardToVoiceMail': 'True',
        'callingSearchSpaceName': ('<your css here>')
        },
    'callForwardNoCoverageInt':
        {
        'forwardToVoiceMail': 'True',
        'callingSearchSpaceName': ('<your css here>')
        },
    'callForwardOnFailure':
        {
        'forwardToVoiceMail': 'True',
        'callingSearchSpaceName': ('<your css here>')
        },
    'callForwardNotRegistered':
        {
        'forwardToVoiceMail': 'True',
        'callingSearchSpaceName': ('<your css here>')
        },
    'callForwardNotRegisteredInt':
        {
        'forwardToVoiceMail': 'True',
        'callingSearchSpaceName': ('<your css here>')
        }
}

# Execute the addLine request
try:
    resp = service.addLine( line )

except Fault as err:
    print( f'Zeep error: addLine: { err }' )
    sys.exit( 1 ) # If the line already exists in CUCM, it will fail and exit the script here.  This assumes you are wanting a new line and exits script to keep from harming your configuration

print( '\naddLine response:\n' )
print( resp,'\n' )

# Create jabber phone , associating the User and Line
csfName=((firstName + lastName)[:12]) # This limits the CSF name to the appropriate amount of characters limited in CUCM for device name
phone = {
    'name': ( f'CSF{csfName}'),
    'description':  (firstName + ' ' + lastName + ' - Jabber'), # Change this if you want to add a different description for the phone
    'product': 'Cisco Unified Client Services Framework',
    'model': 'Cisco Unified Client Services Framework',
    'class': 'Phone',
    'protocol': 'SIP',
    'protocolSide': 'User',
    'devicePoolName': ('<your DP name here>'),
    'commonPhoneConfigName': ('<your common phone config here>'),
    'commonDeviceConfigName': ('<your common device config here>'),
    'locationName': ('<your location name here>'),
    'mediaResourceListName': ('<your MRGL here>'),
    'useTrustedRelayPoint': 'Default',
    'builtInBridgeStatus': 'Default',
    'sipProfileName': 'Standard SIP Profile',
    'packetCaptureMode': 'None',
    'enableExtensionMobility': 'false',
    'certificateOperation': 'No Pending Operation',
    'deviceMobilityMode': 'Default',
    'subscribeCallingSearchSpaceName': ('<your css here>'),
    'rerouteCallingSearchSpaceName': ('<your css here>'),
    'ownerUserName': (userEmail), # this is where you specify the user name in CUCM (userID), set this to what you normally use as a userID format
    'hlogStatus': 'On',
    'allowCtiControlFlag': 'true',
    'lines': {
        'line': [
            {
                'index': 1,
                'label': (lastName + ', ' + firstName),
                'display': (lastName + ', ' + firstName),
                'displayAscii': (lastName + ', ' + firstName),
                'e164Mask': 'XXXXXXXXXXX', # Change this if you want to mask calls to another number, this will mask the calls with the line # of the device
                'maxNumCalls': '6',
                'busyTrigger': '2',
                'callInfoDisplay': {
                    'callerName': 'false',
                    'callerNumber': 'false',
                    'redirectedNumber': 'true',
                    'dialedNumber': 'false'
                },
                'dirn': {
                    'pattern': (phoneExt),
                    'routePartitionName': ('<your partition here>')
                },
                'associatedEndusers': {
                    'enduser': {
                        'userId': (userEmail) # this is where you specify the user name in CUCM (userID), set this to what you normally use as a userID format
                    }
                }
            }
        ]
    }
}
# Create an Element object from scratch with tag 'videoCapability' and text '0'
videoCapability = etree.Element( 'videoCapability' )
videoCapability.text = '0'

# Append each top-level element to an array
vendorConfig = []
vendorConfig.append( videoCapability )

# Create a Zeep xsd type object of type XVendorConfig from the client object
xvcType = client.get_type( 'ns0:XVendorConfig' )

# Use the XVendorConfig type object to create a vendorConfig object
#   using the array of vendorConfig elements from above, and set as
#   phone.vendorConfig
phone[ 'vendorConfig' ] = xvcType( vendorConfig )

# Execute the addPhone request
try:
    resp = service.addPhone( phone )

except Fault as err:
    print( f'Zeep error: addPhone: { err }' )
    sys.exit( 1 )

print( '\naddPhone response:\n' )
print( resp,'\n' )

# Update User account ot associate CSF to their profile
# Sets selfService # as well as setting primary line to the one you created above in case you are using auto provisioning IVR
try:
    resp = service.updateUser ( 
        userid = (userEmail), 
        selfService = (phoneExt),
        associatedDevices = ( 'CSF' + csfName ),
        extensionsInfo = { 'extension': { 'pattern': phoneExt, 'routePartition': ('<your route partition here>')}}
    )

except Fault as err:
    print( f'Zeep error: updateUser: { err }' )
    sys.exit( 1 )

print( '\nupdateUser response:\n' )
print( resp,'\n' )
