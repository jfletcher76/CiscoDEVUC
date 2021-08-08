# This script will remove a phone and a line from CUCM
# This script has a check to make sure no other devices are associated before removing the line
# If the line is found to be still associated to other devices, it will not try to remove the line and ask you to verify what is left

# As with ANY remove script, USE IT WITH CAUTION
# APIs are powerful and a typo can mean removing one thing or a LOT of things
# Always, if you can test your scripts in a DEV.  I recommend using Cisco's DevNET Sandboxes which you can find in the readme file of this repo

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
WSDL_FILE = '<enter path to your wsdl file here>'

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

# Gather user input
print('This script is to remove an ANON phone only.  Do not run this script')
print('if you are NOT wanting to remove the line from CUCM')
print('')
print('If you run this script and remove a line that might be associated to')
print('other things you could break those things in CUCM')
print('')
phoneMAC=input('Enter Phone MAC Address: ')
print('')

# Gets the phone info and find out what extension is assigned to line 1 and what partition line is in
try:
    resp = service.getPhone ( name = phoneMAC )
except:
    print('')
    print('Phone not found in system, exiting script')
    print('')
    sys.exit(0)

# Parse and assign variables for the removal process
phonePartition = resp["return"]["phone"]["lines"]["line"][0]["dirn"]["routePartitionName"]["_value_1"]
phoneExt = resp["return"]["phone"]["lines"]["line"][0]["dirn"]["pattern"]

print('')
print('This will remove this phone')
print('')
print('Phone MAC: ' + phoneMAC)
print('Phone Extension: ' + phoneExt + ' in partition ' + phonePartition)
print('')
executeReq=input('Do you wish to continue? (Y/N): ')


if executeReq.upper() == 'Y':
    # Execute the removePhone request
    resp = service.removePhone( name = phoneMAC )
    print(resp)
else:
    print('')
    print('Verification failed, exiting script')
    sys.exit(0)

# run resp to get line info
resp = service.getLine (pattern = phoneExt, routePartitionName = phonePartition)

# parse response and look for device associations
deviceAssociation = resp["return"]["line"]["associatedDevices"]
# change reponse to true if has data and false if null
deviceCheck=bool(deviceAssociation)
# check if device association has nothing in it (false) then remove line, otherwise device probably has stuff associated and script aborts so you can go investigate what elese is associated
if deviceCheck == False:
    print('No devices associated to number, removing line from CUCM')
    print('')
    verifyRemove=input('Are you sure you want to remove the extension? (Y/N): ')
    if verifyRemove.upper() == 'Y':
        resp = service.removeLine(pattern = phoneExt, routePartitionName = phonePartition)
        print('')
        print('Extension Removed')
    else:
        print('')
        print('Aboring extension removal and moving to end of script')
else:
    print('Extension still has devices associated, please investigate.  Extension will not be removed.')
    print('')
    print('These devices are: ')
    print('-------------------------------------------------')
    print(deviceAssociation)
    sys.exit()

print('')
print('JOB COMPLETE!!')