# Just adds a line for now, adding phone next

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
WSDL_FILE = 'C:\Software\CUCM WSDL\AXLAPI.wsdl'

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
print('Add ANON Phone Script')
print('')
siteCode=input('Enter 4 Digit Site Code: ')
print('')
locationType=input('AUC or HQ? : ')
print('')
globalName=(siteCode + '_' + locationType)
MAC=input('Enter MAC Address: ')
print('')
print('Next line asks for Display Name which will be what the phone')
print('will have as description and caller ID info.  This would be something')
print('like Front Office or Security')
print('')
phoneName=input('Enter Phone Display Name for caller ID and labeling (Do NOT use side code, script will inject that for you): ')
print('')
phoneExt=input('Enter the extension you want to add to phone: ')
print('')
deviceType=input('Is this a 7841 or an 8851?: ')
print('')
phoneDesc=( phoneName + ' - Phone' )
softKey=( 'Adesa Auction Softkey' )
devicePool=( globalName + '_DP' )
commonDC=( globalName + '_CDC' )
commonPhoneConfig=( globalName + ' Common Phone Profile')
deviceCSS=( 'DEV_' + globalName + '_CSS' )
loc=( globalName + '_LOC' )
#ownerUser=( siteCode + '_CUCM_ANON' )
hLog=('On')
allowCTI=('True')
sipProfile=( 'Standard SIP Profile' )
errCount = 0

if deviceType == '7841':
    buttonTemplate=( 'Adesa Auction - 7841 1 Line 10 SD' )
    securityProfile=( 'Cisco 7841 - Standard SIP Non-Secure Profile' )
    phoneModel = 'Cisco 7841'
else:
    buttonTemplate=( '8851 Reception - 4 Line - 6 SD - Side Car' )
    securityProfile=( 'Cisco 8851 - Standard SIP Non-Secure Profile' )
    phoneModel = 'Cisco 8851'

# Execute the removePhone request
try:
    resp = service.removePhone( name = ('SEP' + MAC ) )

except Fault as err:
    print( f'Zeep error: removePhone: { err }' )
    errCount = 1
    
if errCount == 0:
    print( '\nremovePhone response:\n' )
    print( resp,'\n' )

# Create a test Line
line = {
    'pattern': (phoneExt),
    'description': (siteCode + ' ' + phoneName),
    'alertingName': (siteCode + ' ' + phoneName),
    'asciiAlertingName': (siteCode + ' ' + phoneName),
    'usage': 'Device',
    'routePartitionName': ('GLOBAL_DN_PT'),
    'voiceMailProfileName': 'KAR_VM',
    'shareLineAppearanceCssName': (globalName + '_LD_CSS'),
    'callForwardAll':
        {
        'forwardToVoiceMail': 'False',
        'callingSearchSpaceName': ('DEV_' + globalName + '_CSS'),
        'secondaryCallingSearchSpaceName': ('DEV_' + globalName + '_CSS')
        },
    'callForwardBusy':
        {
        'forwardToVoiceMail': 'True',
        'callingSearchSpaceName': ('DEV_' + globalName + '_CSS')
        },
    'callForwardBusyInt':
        {
        'forwardToVoiceMail': 'True',
        'callingSearchSpaceName': ('DEV_' + globalName + '_CSS')
        },
    'callForwardNoAnswer':
        {
        'forwardToVoiceMail': 'True',
        'callingSearchSpaceName': ('DEV_' + globalName + '_CSS')        
        },
    'callForwardNoAnswerInt':
        {
        'forwardToVoiceMail': 'True',
        'callingSearchSpaceName': ('DEV_' + globalName + '_CSS')        
        },
    'callForwardNoCoverage':
        {
        'forwardToVoiceMail': 'True',
        'callingSearchSpaceName': ('DEV_' + globalName + '_CSS')         
        },
    'callForwardNoCoverageInt':
        {
        'forwardToVoiceMail': 'True',
        'callingSearchSpaceName': ('DEV_' + globalName + '_CSS')         
        },
    'callForwardOnFailure':
        {
        'forwardToVoiceMail': 'True',
        'callingSearchSpaceName': ('DEV_' + globalName + '_CSS')         
        },
    'callForwardNotRegistered':
        {
        'forwardToVoiceMail': 'True',
        'callingSearchSpaceName': ('DEV_' + globalName + '_CSS')         
        },
    'callForwardNotRegisteredInt':
        {
        'forwardToVoiceMail': 'True',
        'callingSearchSpaceName': ('DEV_' + globalName + '_CSS')         
        }
}

# Execute the addLine request
try:
    resp = service.addLine( line )

except Fault as err:
    print( f'Zeep error: addLine: { err }' )
    sys.exit( 1 )

print( '\naddLine response:\n' )
print( resp,'\n' )

# Create a test phone, associating the line from above
phone = {
    'name':  ('SEP' + MAC),
    'product': (phoneModel),
    'model': (phoneModel),
    'class': 'Phone',
    'protocol': 'SIP',
    'protocolSide': 'User',
    'devicePoolName': (globalName + '_DP'),
    'description': (siteCode + ' ' + phoneName + ' - Phone'),
    'callingSearchSpaceName': ('DEV_' + globalName + '_CSS'),
    'subscribeCallingSearchSpaceName': ('DEV_' + globalName + '_CSS'),
    'rerouteCallingSearchSpaceName': ('DEV_' + globalName + '_CSS'),
    'commonDeviceConfigName': (commonDC),
    'commonPhoneConfigName': (commonPhoneConfig),
    'softkeyTemplateName': (softKey),
    'phoneTemplateName': (buttonTemplate),
    'locationName': (globalName + '_LOC'),
    'mediaResourceListName': (globalName + '_MRGL'),
    'useTrustedRelayPoint': 'Default',
    'builtInBridgeStatus': 'Default',
    'securityProfileName': (securityProfile),
    'sipProfileName': (sipProfile),
    'packetCaptureMode': 'None',
    'certificateOperation': 'No Pending Operation',
    'deviceMobilityMode': 'Default',
    'allowCtiControlFlag': 'true',
    'hlogStatus': 'On',
    'lines': {
        'line': [
            {
                'index': 1,
                'label': (siteCode + ' ' + phoneName),
                'display': (siteCode + ' ' + phoneName),
                'displayAscii': (siteCode + ' ' + phoneName),
                'e164Mask': 'XXXXXXXXXXX',
                'maxNumCalls': '4',
                'busyTrigger': '2',
                'callInfoDisplay': {
                    'callerName': 'false',
                    'callerNumber': 'false',
                    'redirectedNumber': 'true',
                    'dialedNumber': 'false'
                },
                'dirn': {
                    'pattern': (phoneExt),
                    'routePartitionName': 'GLOBAL_DN_PT'
                }
            }
        ]
    }
}

# Execute the addPhone request
try:
    resp = service.addPhone( phone )

except Fault as err:
    print( f'Zeep error: addPhone: { err }' )
    sys.exit( 1 )

print( '\naddPhone response:\n' )
print( resp,'\n' )