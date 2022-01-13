# PLEASE READ FIRST
# You will need one folder.
# You will need an input file as well, currently points to input3.csv
# Folder1: C:\PythonInput - this is where you store your input file
# Change "CUCM" items to match your device pools, search spaces, partitions, VM profiles, etc

import csv
from requests.auth import HTTPBasicAuth
#from http.client import HTTPConnection
from lxml import etree
from requests import Session
from requests.auth import HTTPBasicAuth
from zeep import Client, Settings, Plugin
from zeep.transports import Transport
from zeep.exceptions import Fault
import sys
import urllib3
# For the file select pop up module
import PySimpleGUI as sg
# Edit .env file to specify your Webex site/user details
import os
from dotenv import load_dotenv
load_dotenv()
import random


# Change to true to enable output of request/response headers and XML
DEBUG = False

# The WSDL is a local file in the working directory, see README
# WSDL_FILE = 'schema/AXLAPI.wsdl'
# WSDL_FILE = 'C:\Software\CUCM WSDL\AXLAPI.wsdl'
WSDL_FILE = '<insert your wsdl location here>'

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

# Code to execute pop up box for file selection on your local machine
if len(sys.argv) == 1:
    fname = sg.popup_get_file('Choose your file')
else:
    fname = sys.argv[1]

with open(fname) as f:
    reader = csv.reader(f)
    for userEmail, firstName, lastName, phoneExt, globalName, needExt in reader:
        if needExt.upper() == 'Y':
            # Create The Line
            line = {
                'pattern': (phoneExt),
                'description': (f'{lastName}, {firstName}'),
                'alertingName': (f'{lastName}, {firstName}'),
                'asciiAlertingName': (f'{lastName}, {firstName}'),
                'usage': 'Device',
                'routePartitionName': 'CUCM_DN_PT',
                'voiceMailProfileName': 'CUCM_VM',
                'shareLineAppearanceCssName': ('CUCM_HQ_LD_CSS'),
                'callForwardAll':
                    {
                    'forwardToVoiceMail': 'False',
                    'callingSearchSpaceName': ('DEV_CUCM_HQ_CSS'),
                    'secondaryCallingSearchSpaceName': ('DEV_CUCM_HQ_CSS')
                    },
                'callForwardBusy':
                    {
                    'forwardToVoiceMail': 'True',
                    'callingSearchSpaceName': ('DEV_CUCM_HQ_CSS')
                    },
                'callForwardBusyInt':
                    {
                    'forwardToVoiceMail': 'True',
                    'callingSearchSpaceName': ('DEV_CUCM_HQ_CSS')
                    },
                'callForwardNoAnswer':
                    {
                    'forwardToVoiceMail': 'True',
                    'callingSearchSpaceName': ('DEV_CUCM_HQ_CSS')        
                    },
                'callForwardNoAnswerInt':
                    {
                    'forwardToVoiceMail': 'True',
                    'callingSearchSpaceName': ('DEV_CUCM_HQ_CSS')        
                    },
                'callForwardNoCoverage':
                    {
                    'forwardToVoiceMail': 'True',
                    'callingSearchSpaceName': ('DEV_CUCM_HQ_CSS')         
                    },
                'callForwardNoCoverageInt':
                    {
                    'forwardToVoiceMail': 'True',
                    'callingSearchSpaceName': ('DEV_CUCM_HQ_CSS')         
                    },
                'callForwardOnFailure':
                    {
                    'forwardToVoiceMail': 'True',
                    'callingSearchSpaceName': ('DEV_CUCM_HQ_CSS')         
                    },
                'callForwardNotRegistered':
                    {
                    'forwardToVoiceMail': 'True',
                    'callingSearchSpaceName': ('DEV_CUCM_HQ_CSS')         
                    },
                'callForwardNotRegisteredInt':
                    {
                    'forwardToVoiceMail': 'True',
                    'callingSearchSpaceName': ('DEV_CUCM_HQ_CSS')         
                    }
            }

            # Execute the addLine request
            try:
                resp = service.addLine( line )

            except Fault as err:
                print( f'Zeep error: addLine: { err }' )
                sys.exit( 1 )
        else:
            print('')
            print('Import files states user does not need line created, moving on')
            print('')

        if needExt.upper() == 'Y':
            print( '\naddLine response:\n' )
            print( resp,'\n' )

        # If you have multiple device pools because you have multiple sites and active subscribers this will help balance those groups.  Remove if you don't need it
        # Then you an just assign devicePool = '<your device pool>'
        if globalName == 'CUCM_HQ':
            rando=random.randint(1,1000)
            iRemainder = (rando % 2)
            if iRemainder == 0:
                devicePool = (f'{globalName}_PHONES_DP1')
            else:
                devicePool = (f'{globalName}_PHONES_DP2')
        else:
            devicePool=(f'{globalName}_DP')

        # Create jabber phone , associating the User and Line
        csfName=((firstName + lastName)[:12])
        phone = {
            'name': (f'CSF{csfName}'),
            'description':  (f'{firstName} {lastName} - Jabber'),
            'product': 'Cisco Unified Client Services Framework',
            'model': 'Cisco Unified Client Services Framework',
            'class': 'Phone',
            'protocol': 'SIP',
            'protocolSide': 'User',
            'devicePoolName': (devicePool),
            'callingSearchSpaceName': (f'DEV_{globalName}_CSS'),
            'commonPhoneConfigName': 'CUCM_HQ Common Phone Profile',
            'commonDeviceConfigName': 'CUCM_HQ_CDC',
            'locationName': 'CUCM_HQ_LOC',
            'mediaResourceListName': 'CUCM_HQ_MRGL',
            'useTrustedRelayPoint': 'Default',
            'builtInBridgeStatus': 'Default',
            'sipProfileName': 'Standard SIP Profile',
            'packetCaptureMode': 'None',
            'enableExtensionMobility': 'false',
            'certificateOperation': 'No Pending Operation',
            'deviceMobilityMode': 'Default',
            'subscribeCallingSearchSpaceName': 'DEV_CUCM_HQ_CSS',
            'rerouteCallingSearchSpaceName': 'DEV_CUCM_HQ_CSS',
            'ownerUserName': (userEmail),
            'hlogStatus': 'On',
            'allowCtiControlFlag': 'true',
            'lines': {
                'line': [
                    {
                        'index': 1,
                        'label': (f'{lastName}, {firstName}'),
                        'display': (f'{lastName}, {firstName}'),
                        'displayAscii': (f'{lastName}, {firstName}'),
                        'e164Mask': 'XXXXXXXXXXX',
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
                            'routePartitionName': 'CUCM_DN_PT'
                        },
                        'associatedEndusers': {
                            'enduser': {
                                'userId': (userEmail)
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

        try:
            resp = service.updateUser ( 
                userid = (userEmail), 
                selfService = (phoneExt),
                associatedDevices = (f'CSF{csfName}'),
                extensionsInfo = { 'extension': { 'pattern': phoneExt, 'routePartition': ('CUCM_DN_PT')}}
            )

        except Fault as err:
            print( f'Zeep error: updateUser: { err }' )
            sys.exit( 1 )

        print( '\nupdateUser response:\n' )
        print( resp,'\n' )

print('')
print('JOB COMPLETE')
