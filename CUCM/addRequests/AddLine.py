# This script simply adds a directory number in CUCM.  This won't add a device or anything else

from lxml import etree
from requests import Session
from requests.auth import HTTPBasicAuth
from zeep import Client, Settings, Plugin, xsd
from zeep.transports import Transport
from zeep.exceptions import Fault
import sys
import urllib3

# Edit .env file to specify your site/user details
import os
from dotenv import load_dotenv
load_dotenv()

# Change to true to enable output of request/response headers and XML
DEBUG = False

# The WSDL is a local file in the working directory, see README
# WSDL_FILE = 'schema/AXLAPI.wsdl'
WSDL_FILE = '<point this to your wsdl file>'

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

phoneExt=input('Enter a Directory Number: ')
siteCode=input('Enter Site Code: ')
locationType=input('Enter Location Type: ')
globalName=(f'{siteCode}_{locationType}')
firstname=input('Enter First Name: ')
lastname=input('Enter Last Name: ')

# Creates Line
# You must specify your own calling search spaces and partitions below in between the < > areas
line = {
    'pattern': (phoneExt),
    'description': (f'{lastname}, {firstname}'),
    'alertingName': (f'{lastname}, {firstname}'),
    'asciiAlertingName': (f'{lastname}, {firstname}'),
    'usage': 'Device',
    'routePartitionName': ('<your parition here>'),
    'voiceMailProfileName': ('<your VM profile here>'),
    'shareLineAppearanceCssName': ('<your CSS here'),
    'callForwardAll':
        {
        'forwardToVoiceMail': 'False',
        'callingSearchSpaceName': ('<your CSS here>'),
        'secondaryCallingSearchSpaceName': ('<your CSS here>')
        },
    'callForwardBusy':
        {
        'forwardToVoiceMail': 'True',
        'callingSearchSpaceName': ('<your CSS here>')
        },
    'callForwardBusyInt':
        {
        'forwardToVoiceMail': 'True',
        'callingSearchSpaceName': ('<your CSS here>')
        },
    'callForwardNoAnswer':
        {
        'forwardToVoiceMail': 'True',
        'callingSearchSpaceName': ('<your CSS here>')        
        },
    'callForwardNoAnswerInt':
        {
        'forwardToVoiceMail': 'True',
        'callingSearchSpaceName': ('<your CSS here>')        
        },
    'callForwardNoCoverage':
        {
        'forwardToVoiceMail': 'True',
        'callingSearchSpaceName': ('<your CSS here>')         
        },
    'callForwardNoCoverageInt':
        {
        'forwardToVoiceMail': 'True',
        'callingSearchSpaceName': ('<your CSS here>')         
        },
    'callForwardOnFailure':
        {
        'forwardToVoiceMail': 'True',
        'callingSearchSpaceName': ('<your CSS here>')         
        },
    'callForwardNotRegistered':
        {
        'forwardToVoiceMail': 'True',
        'callingSearchSpaceName': ('<your CSS here>')         
        },
    'callForwardNotRegisteredInt':
        {
        'forwardToVoiceMail': 'True',
        'callingSearchSpaceName': ('<your CSS here>')         
        }
}

# Execute the addLine request
try:
    resp = service.addLine( line )

except Fault as err:
    print( f'Zeep error: addLine: { err }' )
    sys.exit( 1 )

# Prints the response to your request above to see if it passed or failed
print( '\naddLine response:\n' )
print( resp,'\n' )