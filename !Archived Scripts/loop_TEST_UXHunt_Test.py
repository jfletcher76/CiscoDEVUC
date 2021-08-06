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
print('The script will create the Auction UX Hunt Groups')
print('Items Created: Line Group, Hunt List, Hunt Pilot')
print('Make sure you have your 4 digit site code and pilot number for each dept')
print('')
gatherInfo=input('If you do not have that info, type STOP in all caps to exit script, else hit enter to continue: ')

if gatherInfo == 'STOP' :
    print('Script Aborting')
    exit()
else:
    print('Script Continuing to gahter information stage')

print('')
siteCode=input('Enter 4 Digit Site Code: ')
extensionAR=input('Enter AR Pilot Extension: ')
extensionARB=input('Enter ARB Pilot Extension: ')
extensionFLEET=input('Enter FLEET Pilot Extension: ')
extensionGATEPASS=input('Enter GATEPASS Pilot Extension: ')
extensionINSPECT=input('Enter INSPECT Pilot Extension: ')
extensionREDEMPTIONS=input('Enter REDEMPTIONS Pilot Extension: ')
extensionSALES=input('Enter SALES Pilot Extension: ')
extensionTITLES_REG=input('Enter TITLES Pilot Extension: ')
print('')
print('')

print('--------------------------------------------------------------------')
print('----------------------SETTINGS VERIFICATIONS------------------------')
print('--------------------------------------------------------------------')
print('')
print('Site Code: ' + siteCode)
print('AR Extension: ' + extensionAR)
print('ARB Extension: ' + extensionARB)
print('FLEET Extension: ' + extensionFLEET)
print('GATEPASS Extension: ' + extensionGATEPASS)
print('INSPECT Extension: ' + extensionINSPECT)
print('REDEMPTIONS Extension: ' + extensionREDEMPTIONS)
print('SALES Extension: ' + extensionSALES)
print('TITLES Extension: ' + extensionTITLES_REG)
print('')
print('--------------------------------------------------------------------')
print('')
verifySettings=input('If settings look correct type VERIFY to continue to build location, otherwise press enter to exit: ')

if verifySettings != 'VERIFY' :
    print('Script Aborting')
    exit()
else:
    print('Script will run with above settings')