# This script takes a line group name and shows you all members of the line group and their logged in/out status
# Line group input must be the exact case you have it in CUCM to work.  

from lxml import etree
from requests import Session
from requests.auth import HTTPBasicAuth
from zeep import Client, Settings, Plugin, xsd
from zeep.transports import Transport
from zeep.exceptions import Fault
import sys
import urllib3
import csv

# Edit .env file to specify your Webex site/user details
import os
from dotenv import load_dotenv
load_dotenv()

# Change to true to enable output of request/response headers and XML
DEBUG = False

# The WSDL is a local file in the working directory, see README
# WSDL_FILE = 'schema/AXLAPI.wsdl'
WSDL_FILE = '<path to wsdl file here>'


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
lineGroup = input("Enter Line Group Name: ")
print('')

# Create an object containing the raw SQL query to run
sql = '''select lg.name as LineGroupName, n.dnorpattern as LineMember, n.description as LineDescription,dhd.hlog as LoggedIn, d.name as HardPhoneName FROM linegroup as lg inner join linegroupnumplanmap as lgmap on lgmap.fklinegroup=lg.pkid inner join numplan as n on lgmap.fknumplan = n.pkid inner join devicenumplanmap as dmap on dmap.fknumplan = n.pkid inner join device as d on dmap.fkdevice=d.pkid left join extensionmobilitydynamic as emd on emd.fkdevice_currentloginprofile=dmap.pkid left join device as dp on emd.fkdevice_currentloginprofile=dp.pkid join devicehlogdynamic as dhd on dhd.fkdevice=d.pkid where lg.name = "''' + lineGroup + '''" order by lg.name'''

# Execute the executeSQLQuery request
resp = service.executeSQLQuery( sql )

# Create a simple report of the SQL response
print( 'Logged in users belonging to ' + lineGroup )
print( 'Line Group, Extension, User Name, Logged In, Device Name')
print( '==================================================')

for rowXml in resp[ 'return' ][ 'row' ]:

    lgName = rowXml[ 0 ].text
    extNum = rowXml[ 1 ].text
    userName = rowXml[ 2 ].text
    loggedIn = rowXml[ 3 ].text
    deviceName = rowXml[ 4 ].text
    print( lgName, extNum, userName, loggedIn, deviceName )