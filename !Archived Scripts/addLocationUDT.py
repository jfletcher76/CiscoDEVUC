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

# this script adds a universal line template to CUCM

print('')
print('When entering in letters or words for inputs always use CAPS unless otherwise directed')
print('Some areas will specify if you need to type something in a specific way')
print('')
siteCode=input('Enter 4 Digit Site Code: ')
print('')
locationType=input('AUC or HQ? : ')
print('')
globalName=(siteCode + '_' + locationType)

addUDT = {
    'name': (globalName + '_AutoProv_UDT'),
    'deviceDescription': ('#FN# #LN# - Phone'),
    'devicePool': (globalName + '_DP'),
    'deviceSecurityProfile': 'Universal Device Template - Model-independent Security Profile',
    'sipProfile': 'Standard SIP Profile',
    'phoneButtonTemplate': 'Auction Universal Template',
    'callingSearchSpace': ('DEV_' + globalName + '_CSS'),
    'reroutingCallingSearchSpace': ('DEV_' + globalName + '_CSS'),
    'subscribeCallingSearchSpaceName': ('DEV_' + globalName + '_CSS'),
    'useDevicePoolCallingPartyTransformationCSSforInboundCalls': 'true',
    'useDevicePoolCallingPartyTransformationCSSforOutboundCalls': 'true',
    'commonPhoneProfile': (globalName + ' Common Phone Profile'),
    'commonDeviceConfiguration': (globalName + '_CDC'),
    'softkeyTemplate': 'Adesa Auction Softkey',
    'phonePersonalization': 'Default',
    'outboundCallRollover': 'No Rollover',
    'mtpPreferredOriginatingCodec': '711ulaw',
    'speeddials':
    {
        'speeddial':
        {
            'dirn': '9999',
            'label': 'Overhead Paging',
            'index': '1'
        }
    },
#    'lines':
#    {
#        'line':
#        {
#            'index': '1',
#            'dirn':
#            {
#                'pattern': '15559998888',
#                'routePartitionName': 'GLOBAL_DN_PT'
#            },
#            'label': '#LN#, #FN#',
#            'display': '#LN#, #FN#',
#            'e164Mask': 'XXXXXXXXXXX',
#            'maxNumCalls': '4',
#            'busyTrigger': '2',
#            'missedCallLogging': 'true',
#            'audibleMwi': 'Default',
#            'callInfoDisplay':
#            {
#                'callerName': 'false',
#                'callerNumber': 'false',
#                'redirectedNumber': 'true',
#                'dialedNumber': 'false'
#            }
#        }
#    },
    'useTrustedRelayPoint': 'Default',
    'certificateOperation': 'No Pending Operation',
    'authenticationMode': 'By Null String',
    'keySize': '2048',
    'servicesProvisioning': 'Default',
    'packetCaptureMode': 'None',
    'userLocale': 'English United States',
    'mlppIndication': 'Off',
    'mlppPreemption': 'Default',
    'dndOption': 'Ringer Off',
    'blfPresenceGroup': 'Standard Presence Group',
    'blfAudibleAlertSettingPhoneBusy': 'Default',
    'blfAudibleAlertSettingPhoneIdle': 'Default',
    'location': (globalName + '_LOC'),
    'deviceMobilityMode': 'Default',
    'mediaResourceGroupList': (globalName + '_MRGL'),
    'ownerUserId': 'Current Device Owner' + "'" + 's User ID',
    'joinAcrossLines': 'Default',
    'alwaysUsePrimeLine': 'Default',
    'alwaysUsePrimeLineForVoiceMessage': 'Default',
    'singleButtonBarge': 'Default',
    'builtInBridge': 'Default',
    'allowControlOfDeviceFromCti': 'true',
    'enableExtensionMobility': 'true',
    'privacy': 'Default',
    'loggedIntoHuntGroup': 'true',
    'retryVideoCallAsAudio': 'false',
    'services':
    {
        'service':
        {
            'telecasterServiceName': 'Extension Mobility',
            'name': 'Extension Mobility'
        }
    }
}

# Execute the addUniversalDeviceTemplate request
try:
    resp = service.addUniversalDeviceTemplate( addUDT )

except Fault as err:
    print( f'Zeep error: addUniversalDeviceTemplate: { err }' )
    sys.exit( 1 )

print( '\naddUniversalDeviceTemplate response:\n' )
print( resp,'\n' )