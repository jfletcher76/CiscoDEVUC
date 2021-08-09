# This script will interate through a csv of translation patterns and output what they are translating to
# Gotta change your partition

# This is a good script to use if you want to see what all translation patterns are pointing to

from lxml import etree
from requests import Session
from requests.auth import HTTPBasicAuth
from zeep import Client, Settings, Plugin, xsd
from zeep.transports import Transport
from zeep.exceptions import Fault
import sys
import urllib3

import PySimpleGUI as sg
import csv

# Edit .env file to specify your Webex site/user details
import os
from dotenv import load_dotenv
load_dotenv()

# Change to true to enable output of request/response headers and XML
DEBUG = False

# The WSDL is a local file in the working directory, see README
# WSDL_FILE = 'schema/AXLAPI.wsdl'
WSDL_FILE = '<your wsdl file path here>'


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
sg.theme("SystemDefault")
layout = [[sg.T("")], [sg.Text("Choose a file: "), sg.Input(), sg.FileBrowse(key="-IN-")],[sg.Button("Submit")]]

###Building Window
window = sg.Window('CSV File Browser', layout, size=(600,150))
    
event, values = window.read()
if event == sg.WIN_CLOSED or event=="Exit":
    sys.exit(1)
elif event == "Submit":
    window.close()

# Asks for the location and file name to write the output too, comment out next two lines if you don't want to do this
# You will also need to remove file=outF from your resp
filePath = input('Get file: ')
outF = open(filePath, 'a') # 'a' for append 'w' for write

# Iterates trough your .csv file to pull calledparty mask from translation patterns
# This script will write the output to a file.  Modify it if you want to print to screen by 
# removing the file=outF from the resp statement along with the final , after ['description']
with open(values["-IN-"]) as f:
    reader = csv.reader(f)
    for xLate, in reader:
        resp = service.getTransPattern(pattern = xLate, routePartitionName = '<your partition here>' )
        print(resp['return']['transPattern']['pattern'], 
        resp['return']['transPattern']['calledPartyTransformationMask'],
        resp['return']['transPattern']['description'], 
        file=outF)

outF.close()