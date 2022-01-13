# This script is used to check a group of extensions are valid in CUCM
# If you are needing to find out of a list of extensions exists, load up a CSV file with two columns
# No column headers, column1 = extension, column2 = partition
# Example: 
# 15551231234, PARTITION_A
# 19992359912, PARTITION_B
#
# If you want to check extensions in other partitions you can do so by setting the column2 to the partition you are checking

from lxml import etree
from requests import Session
from requests.auth import HTTPBasicAuth
from zeep import Client, Settings, Plugin, xsd
from zeep.transports import Transport
from zeep.exceptions import Fault
import sys
import urllib3
import csv

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
sg.theme("SystemDefault")
layout = [
    [sg.T("")],
    [sg.Text("Choose a file: "), sg.Input(), sg.FileBrowse(key="-IN-")],
    [sg.Text("Enter output file location and name: "), sg.InputText()],
    [sg.Text('Write to a new file or append to existing?')],
    [sg.Combo(values=('Append', 'New'), default_value='New', readonly=True, k='-COMBO1-')],
    [sg.Text("")],
    [sg.Submit(), sg.Cancel()]
    ]

###Building Window
window = sg.Window('CSV File Browser', layout, size=(600,200))
    
event, values = window.read()
if event == sg.WIN_CLOSED or event=="Exit":
    sys.exit()
elif event == "Submit":
    filePath=values[1]
    fileWrite=values['-COMBO1-']
    window.close()

# sets the file attirube for outF to either w (write) or a (append)
# write will overwrite your file if you have one already, append will.... add to it!
if fileWrite == 'New':
    attrib='w'
else:
    attrib='a'

print(filePath)
outF = open(filePath, attrib)
with open(values["-IN-"]) as f:
    reader = csv.reader(f)
    for phoneExt, phonePart in reader:
        try:
            resp = service.getLine ( pattern = phoneExt, routePartitionName = phonePart )
            lineDescription=resp['return']['line']['description']
            print(f'Extension {phoneExt} exists in CUCM, owned by {lineDescription}.')
            print(f'Extension {phoneExt} exists in CUCM, owned by {lineDescription}.', file=outF)
        except Fault as err:
            print(f'Extension {phoneExt} does not exist, please investigate.')
            print(f'Extension {phoneExt} does not exist, please investigate.', file=outF)

outF.close()
