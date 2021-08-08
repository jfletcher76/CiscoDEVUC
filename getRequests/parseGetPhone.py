# this script parses a getPhone request for various info
# lots of stuff commented out but you can see descriptions for what it does
# could be useful for something you may be trying to do with getPhone

from lxml import etree
from requests import Session
from requests.auth import HTTPBasicAuth
from zeep import Client, Settings, Plugin, xsd
from zeep.transports import Transport
from zeep.exceptions import Fault
import sys
import urllib3
import json

# Edit .env file to specify your Webex site/user details
import os
from dotenv import load_dotenv
load_dotenv()

# Change to true to enable output of request/response headers and XML
DEBUG = False

# The WSDL is a local file in the working directory, see README
# WSDL_FILE = 'schema/AXLAPI.wsdl'
# WSDL_FILE = 'C:\Software\CUCM WSDL\AXLAPI.wsdl'
WSDL_FILE = '<enter path to wsdl here>'

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

# Gather yo facts!
print('')
phoneMAC=input('Enter MAC address of phone here: ')
print('')

# Run yo get!
resp = service.getPhone ( name = ( f'SEP{phoneMAC}' ) )

# Uncomment this to see everything in the response
#print(resp)
# Parse and Assign data to variables!!
#phoneDesc = resp["return"]["phone"]["description"]
phoneExt = resp["return"]["phone"]["lines"]["line"][0]["dirn"]["pattern"]
# ["_value_1"] returns the friendly name you would see in GUI
# If you want UUID instead, change ["_value_1"] to ["uuid"]
#secProfile = resp["return"]["phone"]["securityProfileName"]["_value_1"]
# You will get all values if you leave off the last piece of secProfile, like below
# This shows friendly name and UUID in response if that is all you want to see
#secProfile = resp["return"]["phone"]["securityProfileName"]

# Print your parse!
print(phoneExt)
#print(phoneDesc)
#print(secProfile)
# print(secProfile) alone gives you both UUID and Friendly name.  So if you are trying
# to get the UUID out of your response, then uncomment print(secProfile.uuid)
#print(secProfile._value_1)
#print(secProfile.uuid)
