# This script will get the info of a line and parse the response to get devices associated
# the list of devices associated are then printed, helpful to use this in other scripts 

# from lxml import etree # uncomment etree when you need it
from requests import Session
from requests.auth import HTTPBasicAuth
from zeep import Client, Settings
from zeep.transports import Transport
import sys
import urllib3

# Edit .env file to specify your Webex site/user details
import os
from dotenv import load_dotenv
load_dotenv()

# Change to true to enable output of request/response headers and XML
DEBUG = False

# The WSDL is a local file in the working directory.  You can have it in different spots, see examples below
# WSDL_FILE = 'schema/AXLAPI.wsdl'
WSDL_FILE = '<path to wsdl here>'

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

# Create the Zeep client with the specified settings
client = Client( WSDL_FILE, settings = settings, transport = transport
        )

# Create the Zeep service binding to AXL at the specified CUCM
service = client.create_service( '{http://www.cisco.com/AXLAPIService/}AXLAPIBinding',
                                f'https://{os.getenv( "CUCM_ADDRESS" )}:8443/axl/' )

# enter line number and route partition you want to request device association
# route partition must be the exact case you have it in CUCM
print('')
phoneExt=input('Enter extension: ')
print('')
routePartition=input('Enter route partition: ')
print('')

# run resp to get line info
resp = service.getLine (pattern = phoneExt, routePartitionName = routePartition)
# parse response and look for device associations
deviceAssociation = resp["return"]["line"]["associatedDevices"]
print('')
print(deviceAssociation)
print('')