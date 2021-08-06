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
print('Add Location to CUCM Script')
print('')
# This section sets the static variables and gathers information for the other variables needed
print('When entering in letters or words for inputs always use CAPS unless otherwise directed')
print('Some areas will specify if you need to type something in a specific way')
print('')
siteCode=input('Enter 4 Digit Site Code: ')
print('')
locationType=input('AUC or HQ? : ')
print('')
globalName=(siteCode + '_' + locationType)
#timeZone=input('Enter Site TimeZone - EST-EDT, CST-CDT, MST-MDT, PST-PDT, ADT-STJ, AKST-AKDT, AST-ADT: ')
#print('')
#print('Available Softkeys: KAR User with DND, Adesa Auction Softkey, AFC Softkey')
#print('Use the same capitalization as you see above in your input below')
#print('')
#softKey=input('Enter softkey template from above: ')
#print('')
#siteXlate=input('Enter 4 digit translation pattern using all caps for Xs in mask: ')
#print('')
#siteXlatePrefix=input('Enter Site 4 digit prefix Example - 15551233: ')
#print('')
#siteMainLine=input('Enter site main line: ')

# This adds 911 for CER translation 

emergencyPattern = {
    'pattern': '911',
    'description': ( '911 to CER for ' + globalName ),
    'usage': 'Translation',
    'routePartitionName': ( globalName + '_911_PT'),
    'patternUrgency': 'true',
    'calledPartyTransformationMask': '911',
    'callingSearchSpaceName': 'E911_CSS'
}

# Execute add 911 CER Translation 
try:
    resp = service.addTransPattern( emergencyPattern )

except Fault as err:
    print( f'Zeep error: addTransPattern: { err }' )
    sys.exit( 1 )

print( '\naddTransPattern response:\n' )
print( resp,'\n' )