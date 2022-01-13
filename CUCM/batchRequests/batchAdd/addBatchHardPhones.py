# PLEASE READ FIRST
# You will need two folders.
# You will need an input file as well, currently points to input3.csv
# Folder1: C:\PythonInput - this is where you store your input file
# Folder2: C:\PythonOutput - this is where error logging is written
# Modify this script as you see fit if you do not like the above, or insert variables to get the info for the above real time

# This script will go through a CSV file and build phones instead of having to use the clunky batch method in CUCM
# This script assumes you are wanting to associate a user to the phone and will do so using the email variable
# This script also associates the user to the line when adding the phone for presence purposes using the email variable

import time
import csv
from requests.auth import HTTPBasicAuth
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


# Change to true to enable output of request/response headers and XML
DEBUG = False

# The WSDL is a local file in the working directory, see README
# WSDL_FILE = 'schema/AXLAPI.wsdl'
# WSDL_FILE = 'C:\Software\CUCM WSDL\AXLAPI.wsdl'
WSDL_FILE = '<your wsdl file here>'

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

# If lines already exist and you are just building phones to attach to them, select N
print('')
extExists=input('Does the line need to be created?? (Y/N): ')
print('')

with open(fname) as f:
    reader = csv.reader(f)
    for phoneExt, phoneMac, userEmail, firstName, lastName, phoneModel, phoneButtonTemplate, softKey, globalName in reader:
        # set counter to 0 each loop
        errCount = 0
        # Create The Line
        if extExists.upper() == 'Y':
            line = {
                'pattern': (phoneExt),
                'description': (lastName + ', ' + firstName),
                'alertingName': (lastName + ', ' + firstName),
                'asciiAlertingName': (lastName + ', ' + firstName),
                'usage': 'Device',
                'routePartitionName': (f'{globalName}_NULL_PT'),
                'voiceMailProfileName': 'CUCM_VM', # Set your VM profile
                'shareLineAppearanceCssName': (f'{globalName}_LD_CSS'),
                'callForwardAll':
                    {
                    'forwardToVoiceMail': 'False',
                    'callingSearchSpaceName': (f'DEV_{globalName}_CSS'),
                    'secondaryCallingSearchSpaceName': (f'DEV_{globalName}_CSS')
                    },
                'callForwardBusy':
                    {
                    'forwardToVoiceMail': 'True',
                    'callingSearchSpaceName': (f'DEV_{globalName}_CSS')
                    },
                'callForwardBusyInt':
                    {
                    'forwardToVoiceMail': 'True',
                    'callingSearchSpaceName': (f'DEV_{globalName}_CSS')
                    },
                'callForwardNoAnswer':
                    {
                    'forwardToVoiceMail': 'True',
                    'callingSearchSpaceName': (f'DEV_{globalName}_CSS')        
                    },
                'callForwardNoAnswerInt':
                    {
                    'forwardToVoiceMail': 'True',
                    'callingSearchSpaceName': (f'DEV_{globalName}_CSS')        
                    },
                'callForwardNoCoverage':
                    {
                    'forwardToVoiceMail': 'True',
                    'callingSearchSpaceName': (f'DEV_{globalName}_CSS')         
                    },
                'callForwardNoCoverageInt':
                    {
                    'forwardToVoiceMail': 'True',
                    'callingSearchSpaceName': (f'DEV_{globalName}_CSS')         
                    },
                'callForwardOnFailure':
                    {
                    'forwardToVoiceMail': 'True',
                    'callingSearchSpaceName': (f'DEV_{globalName}_CSS')         
                    },
                'callForwardNotRegistered':
                    {
                    'forwardToVoiceMail': 'True',
                    'callingSearchSpaceName': (f'DEV_{globalName}_CSS')         
                    },
                'callForwardNotRegisteredInt':
                    {
                    'forwardToVoiceMail': 'True',
                    'callingSearchSpaceName': (f'DEV_{globalName}_CSS')         
                    }
            }

            # Execute the addLine request
            try:
                resp = service.addLine( line )
                print( '\naddLine response:\n' )
                print( resp,'\n' )

            except Fault as err:
                with open('c:\PythonOutput\ErrorLog.txt', 'a') as errLog: # Set your error log or build a variable to ask and set variable here
                    timeStr = time.strftime("%Y-%m-%d / %H:%M:%S")
                    errMsg=str(err)
                    errCount = 0
                    stringErr=('CUCM: Timestamp: ' + timeStr + ' - ' + userEmail + ': ' + errMsg)
                    # write error log
                    errLog.write(stringErr + "\n")
                print( f'Zeep error: addLine: { err }' )
                #sys.exit( 1 )
        else:
            print('')
            print('Extension creation bypassed, moving on the phone creation')

        # Create phone , associating the User and Line
        if errCount == 0:
            phone = {
                'name': (phoneMac),
                'description':  (firstName + ' ' + lastName + ' - Phone'),
                'product': phoneModel,
                'model': phoneModel,
                'class': 'Phone',
                'protocol': 'SIP',
                'protocolSide': 'User',
                'devicePoolName': (f'{globalName}_DP'),
                'commonPhoneConfigName': (f'{globalName} Common Phone Profile'),
                'commonDeviceConfigName': (f'{globalName}_CDC'),
                'locationName': (f'{globalName}_LOC'),
                'callingSearchSpaceName': (f'DEV_{globalName}_CSS'),
                'mediaResourceListName': (f'{globalName}_MRGL'),
                'useTrustedRelayPoint': 'Default',
                'builtInBridgeStatus': 'Default',
                'softkeyTemplateName': (softKey),
                'phoneTemplateName': (phoneButtonTemplate),
                'securityProfileName': (f'{phoneModel} - Standard SIP Non-Secure Profile'),
                'sipProfileName': 'Standard SIP Profile',
                'packetCaptureMode': 'None',
                'enableExtensionMobility': 'true',
                'certificateOperation': 'No Pending Operation',
                'deviceMobilityMode': 'Default',
                'subscribeCallingSearchSpaceName': (f'DEV_{globalName}_CSS'),
                'rerouteCallingSearchSpaceName': (f'DEV_{globalName}_CSS'),
                'ownerUserName': (userEmail),
                'hlogStatus': 'On',
                'allowCtiControlFlag': 'true',
                    'services': {
                        'service': [
                            {
                                'telecasterServiceName': 'Extension Mobility',
                                'name': 'Extension Mobility',
                                'url': 'http://<your CUCM IP here>:8080/emapp/EMAppServlet?device=#DEVICENAME#&loginType=DN', # validate your EM link and fix this, or remove if you don't want EM on the phones
                                'urlButtonIndex': '0',
                                'phoneServiceCategory': 'Standard IP Phone Service',
                                'phoneServiceCategory': 'XML Serive',
                                'priority': '50'
                            }
                        ]
                    },
                'lines': {
                    'line': [
                        {
                            'index': 1,
                            'label': (lastName + ', ' + firstName),
                            'display': (lastName + ', ' + firstName),
                            'displayAscii': (lastName + ', ' + firstName),
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
                                'routePartitionName': (f'{globalName}_NULL_PT')
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

            # if errCount == 0:
            #     print( '\naddPhone response:\n' )
            #     print( resp,'\n' )

        if errCount == 0:
            # Update User account ot associate phone to their profile
            try:
                resp = service.updateUser ( 
                    userid = (userEmail), 
                    selfService = (phoneExt),
                    associatedDevices = (phoneMac),
                    extensionsInfo = { 'extension': { 'pattern': phoneExt, 'routePartition': (f'{globalName}_NULL_PT')}}
                )

            except Fault as err:
                print( f'Zeep error: updateUser: { err }' )
                sys.exit( 1 )

            # print( '\nupdateUser response:\n' )
            # print( resp,'\n' )

        if errCount == 0:
            print(f'{userEmail} successfully created phone, moving to next line of file')
