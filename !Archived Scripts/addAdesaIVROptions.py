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
print('Add Sites IVR Hunt Group Settings Script')
print('')
print('The script will create the Auction IVR 1-8 Hunt Groups')
print('Items Created: Line Groups, Hunt Lists, Hunt Pilots')
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
option1=input('Enter Sales Option 1 Pilot: ')
option2=input('Enter Fleet and Repo Option 2 Pilot: ')
option3=input('Enter Titles and Reg Option 3 Pilot: ')
option4=input('Enter Arbitration Option 4 Pilot: ')
option5=input('Enter Inspections Option 5 Pilot: ')
option6=input('Enter Transportation Option 6 Pilot: ')
option7=input('Enter Invoices and AR Option 7 Pilot: ')
option8=input('Enter Floating Option 8 Pilot: ')
#frwdTo=input('Enter RONA number: ')
print('')
print('')

print('--------------------------------------------------------------------')
print('----------------------SETTINGS VERIFICATIONS------------------------')
print('--------------------------------------------------------------------')
print('')
print('Site Code: ' + siteCode)
print('Option 1 Extension: ' + option1)
print('Option 2 Extension: ' + option2)
print('Option 3 Extension: ' + option3)
print('Option 4 Extension: ' + option4)
print('Option 5 Extension: ' + option5)
print('Option 6 Extension: ' + option6)
print('Option 7 Extension: ' + option7)
print('Option 8 Extension: ' + option8)
#print('Forward too on no answer: ')
print('')
print('--------------------------------------------------------------------')
print('')
verifySettings=input('If settings look correct type VERIFY to continue to build location, otherwise press enter to exit: ')

if verifySettings != 'VERIFY' :
    print('Script Aborting')
    exit()
else:
    print('Script will run with above settings')

rando=random.randint(1,1000)
iRemainder = (rando % 2)
if iRemainder == 0:
    cucmGroup = 'KAR_CM_GROUP_PDC'
else:
    cucmGroup = 'KAR_CM_GROUP_SPDC'

groupNames = ["Option1", "Option2", "Option3", "Option4", "Option5", "Option6", "Option7", "Option8"]

# Create Line Group
for x in groupNames:
	lineGroup = {
    	'name': ( siteCode + '_' + x + '_LG' ),
    	'distributionAlgorithm': 'Broadcast',
    	'rnaReversionTimeOut': '24',
    	'huntAlgorithmNoAnswer': 'Try next member; then, try next group in Hunt List',
    	'huntAlgorithmBusy': 'Try next member; then, try next group in Hunt List',
    	'huntAlgorithmNotAvailable': 'Try next member; then, try next group in Hunt List'
	}

	# Execute the addLineGroup request
	try:
	    resp = service.addLineGroup( lineGroup )

	except Fault as err:
   		print( f'Zeep error: addLineGroup: { err }' )
   		sys.exit( 1 )

print( '\naddLineGroup response:\n' )
print( resp,'\n' )

# Create Hunt List
for x in groupNames: 
	huntList = {
    	'name': ( siteCode + '_' + x + '_HL'),
    	'description': ( siteCode + '_' + x + '_HL'),
    	'callManagerGroupName': (cucmGroup),
    	'routeListEnabled': 'true',
    	'voiceMailUsage': 'true',
    	'members':
        	{
        	'member':
    	        {
	            'lineGroupName': ( siteCode + '_' + x + '_LG'),
        	    'selectionOrder': "1"
            	}
        	}
	}

	# Execute the addHuntList request
	try:
	    resp = service.addHuntList( huntList )

	except Fault as err:
   		print( f'Zeep error: addHuntList: { err }' )
   		sys.exit( 1 )

print( '\naddHuntList response:\n' )
print( resp,'\n' )

# Create Option1 Pilot Number
huntPilot = {
    'pattern': (option1),
    'description': ( siteCode + '_Option1_Pilot' ),
    'routePartitionName': "Global_DN_PT",
    'patternUrgency': 'false',
    'patternPrecedence': '',
    'provideOutsideDialtone': 'false',
    'huntListName': ( siteCode + '_Option1_HL' ),
    'alertingName': ( '""' + siteCode + '_Option1""'),
    'asciiAlertingName': ( siteCode + '_Option1'),
    'maxHuntduration': '32',
    'blockEnable': 'false',
    'useCallingPartyPhoneMask': ''
# if site needs to route calls that are busy or no answer to another destination, need to include the following and set destination
#    'forwardHuntNoAnswer':
#        {
#        'usePersonalPreferences': 'false',
#        'destination': ( frwdTo ),
#        'callingSearchSpaceName': ( "DEV_" + siteCode +  "_AUC_CSS")
#        },
#    'forwardHuntBusy':
#        {
#        'usePersonalPreferences': 'false',
#        'destination': ( frwdTo ),
#        'callingSearchSpaceName': ( "DEV_" + siteCode +  "_AUC_CSS")
#        }
}

# Execute the addHuntPilot request
try:
    resp = service.addHuntPilot( huntPilot )

except Fault as err:
    print( f'Zeep error: addHuntPilot: { err }' )
    sys.exit( 1 )

print( '\naddHuntPilot response:\n' )
print( resp,'\n' )

# Create Option2 Pilot Number
huntPilot = {
    'pattern': (option2),
    'description': ( siteCode + '_Option2_Pilot' ),
    'routePartitionName': "Global_DN_PT",
    'patternUrgency': 'false',
    'patternPrecedence': '',
    'provideOutsideDialtone': 'false',
    'huntListName': ( siteCode + '_Option2_HL' ),
    'alertingName': ( '""' + siteCode + '_Option2""'),
    'asciiAlertingName': ( siteCode + '_Option2'),
    'maxHuntduration': '32',
    'blockEnable': 'false',
    'useCallingPartyPhoneMask': ''
# if site needs to route calls that are busy or no answer to another destination, need to include the following and set destination
#    'forwardHuntNoAnswer':
#        {
#        'usePersonalPreferences': 'false',
#        'destination': ( frwdTo ),
#        'callingSearchSpaceName': ( "DEV_" + siteCode +  "_AUC_CSS")
#        },
#    'forwardHuntBusy':
#        {
#        'usePersonalPreferences': 'false',
#        'destination': ( frwdTo ),
#        'callingSearchSpaceName': ( "DEV_" + siteCode +  "_AUC_CSS")
#        }
}

# Execute the addHuntPilot request
try:
    resp = service.addHuntPilot( huntPilot )

except Fault as err:
    print( f'Zeep error: addHuntPilot: { err }' )
    sys.exit( 1 )

print( '\naddHuntPilot response:\n' )
print( resp,'\n' )

# Create option3 Pilot Number
huntPilot = {
    'pattern': (option3),
    'description': ( siteCode + '_Option3_Pilot' ),
    'routePartitionName': "Global_DN_PT",
    'patternUrgency': 'false',
    'patternPrecedence': '',
    'provideOutsideDialtone': 'false',
    'huntListName': ( siteCode + '_option3_HL' ),
    'alertingName': ( '""' + siteCode + '_Option3""'),
    'asciiAlertingName': ( siteCode + '_Option3'),
    'maxHuntduration': '32',
    'blockEnable': 'false',
    'useCallingPartyPhoneMask': ''
# if site needs to route calls that are busy or no answer to another destination, need to include the following and set destination
#    'forwardHuntNoAnswer':
#        {
#        'usePersonalPreferences': 'false',
#        'destination': ( frwdTo ),
#        'callingSearchSpaceName': ( "DEV_" + siteCode +  "_AUC_CSS")
#        },
#    'forwardHuntBusy':
#        {
#        'usePersonalPreferences': 'false',
#        'destination': ( frwdTo ),
#        'callingSearchSpaceName': ( "DEV_" + siteCode +  "_AUC_CSS")
#        }
}

# Execute the addHuntPilot request
try:
    resp = service.addHuntPilot( huntPilot )

except Fault as err:
    print( f'Zeep error: addHuntPilot: { err }' )
    sys.exit( 1 )

print( '\naddHuntPilot response:\n' )
print( resp,'\n' )

# Create option4 Pilot Number
huntPilot = {
    'pattern': (option4),
    'description': ( siteCode + '_Option4_Pilot' ),
    'routePartitionName': "Global_DN_PT",
    'patternUrgency': 'false',
    'patternPrecedence': '',
    'provideOutsideDialtone': 'false',
    'huntListName': ( siteCode + '_Option4_HL' ),
    'alertingName': ( '""' + siteCode + '_Option4""'),
    'asciiAlertingName': ( siteCode + '_Option4'),
    'maxHuntduration': '32',
    'blockEnable': 'false',
    'useCallingPartyPhoneMask': ''
# if site needs to route calls that are busy or no answer to another destination, need to include the following and set destination
#    'forwardHuntNoAnswer':
#        {
#        'usePersonalPreferences': 'false',
#        'destination': ( frwdTo ),
#        'callingSearchSpaceName': ( "DEV_" + siteCode +  "_AUC_CSS")
#        },
#    'forwardHuntBusy':
#        {
#        'usePersonalPreferences': 'false',
#        'destination': ( frwdTo ),
#        'callingSearchSpaceName': ( "DEV_" + siteCode +  "_AUC_CSS")
#        }
}

# Execute the addHuntPilot request
try:
    resp = service.addHuntPilot( huntPilot )

except Fault as err:
    print( f'Zeep error: addHuntPilot: { err }' )
    sys.exit( 1 )

print( '\naddHuntPilot response:\n' )
print( resp,'\n' )

# Create option5 Pilot Number
huntPilot = {
    'pattern': (option5),
    'description': ( siteCode + '_Option5_Pilot' ),
    'routePartitionName': "Global_DN_PT",
    'patternUrgency': 'false',
    'patternPrecedence': '',
    'provideOutsideDialtone': 'false',
    'huntListName': ( siteCode + '_option5_HL' ),
    'alertingName': ( '""' + siteCode + '_Option5""'),
    'asciiAlertingName': ( siteCode + '_Option5'),
    'maxHuntduration': '32',
    'blockEnable': 'false',
    'useCallingPartyPhoneMask': ''
# if site needs to route calls that are busy or no answer to another destination, need to include the following and set destination
#    'forwardHuntNoAnswer':
#        {
#        'usePersonalPreferences': 'false',
#        'destination': ( frwdTo ),
#        'callingSearchSpaceName': ( "DEV_" + siteCode +  "_AUC_CSS")
#        },
#    'forwardHuntBusy':
#        {
#        'usePersonalPreferences': 'false',
#        'destination': ( frwdTo ),
#        'callingSearchSpaceName': ( "DEV_" + siteCode +  "_AUC_CSS")
#        }
}

# Execute the addHuntPilot request
try:
    resp = service.addHuntPilot( huntPilot )

except Fault as err:
    print( f'Zeep error: addHuntPilot: { err }' )
    sys.exit( 1 )

print( '\naddHuntPilot response:\n' )
print( resp,'\n' )

# Create Option6 Pilot Number
huntPilot = {
    'pattern': (option6),
    'description': ( siteCode + '_Option6_Pilot' ),
    'routePartitionName': "Global_DN_PT",
    'patternUrgency': 'false',
    'patternPrecedence': '',
    'provideOutsideDialtone': 'false',
    'huntListName': ( siteCode + '_Option6_HL' ),
    'alertingName': ( '""' + siteCode + '_Option6""'),
    'asciiAlertingName': ( siteCode + '_Option6'),
    'maxHuntduration': '32',
    'blockEnable': 'false',
    'useCallingPartyPhoneMask': ''
# if site needs to route calls that are busy or no answer to another destination, need to include the following and set destination
#    'forwardHuntNoAnswer':
#        {
#        'usePersonalPreferences': 'false',
#        'destination': ( frwdTo ),
#        'callingSearchSpaceName': ( "DEV_" + siteCode +  "_AUC_CSS")
#        },
#    'forwardHuntBusy':
#        {
#        'usePersonalPreferences': 'false',
#        'destination': ( frwdTo ),
#        'callingSearchSpaceName': ( "DEV_" + siteCode +  "_AUC_CSS")
#        }
}

# Execute the addHuntPilot request
try:
    resp = service.addHuntPilot( huntPilot )

except Fault as err:
    print( f'Zeep error: addHuntPilot: { err }' )
    sys.exit( 1 )

print( '\naddHuntPilot response:\n' )
print( resp,'\n' )

# Create Option7 Pilot Number
huntPilot = {
    'pattern': (option7),
    'description': ( siteCode + '_Option7_Pilot' ),
    'routePartitionName': "Global_DN_PT",
    'patternUrgency': 'false',
    'patternPrecedence': '',
    'provideOutsideDialtone': 'false',
    'huntListName': ( siteCode + '_Option7_HL' ),
    'alertingName': ( '""' + siteCode + '_Option7""'),
    'asciiAlertingName': ( siteCode + '_Option7'),
    'maxHuntduration': '32',
    'blockEnable': 'false',
    'useCallingPartyPhoneMask': ''
# if site needs to route calls that are busy or no answer to another destination, need to include the following and set destination
#    'forwardHuntNoAnswer':
#        {
#        'usePersonalPreferences': 'false',
#        'destination': ( frwdTo ),
#        'callingSearchSpaceName': ( "DEV_" + siteCode +  "_AUC_CSS")
#        },
#    'forwardHuntBusy':
#        {
#        'usePersonalPreferences': 'false',
#        'destination': ( frwdTo ),
#        'callingSearchSpaceName': ( "DEV_" + siteCode +  "_AUC_CSS")
#        }
}

# Execute the addHuntPilot request
try:
    resp = service.addHuntPilot( huntPilot )

except Fault as err:
    print( f'Zeep error: addHuntPilot: { err }' )
    sys.exit( 1 )

print( '\naddHuntPilot response:\n' )
print( resp,'\n' )

# Create Option8 Pilot Number
huntPilot = {
    'pattern': (option8),
    'description': ( siteCode + '_Option8_Pilot' ),
    'routePartitionName': "Global_DN_PT",
    'patternUrgency': 'false',
    'patternPrecedence': '',
    'provideOutsideDialtone': 'false',
    'huntListName': ( siteCode + '_Option8_HL' ),
    'alertingName': ( '""' + siteCode + '_Option8""'),
    'asciiAlertingName': ( siteCode + '_Option8'),
    'maxHuntduration': '32',
    'blockEnable': 'false',
    'useCallingPartyPhoneMask': ''
# if site needs to route calls that are busy or no answer to another destination, need to include the following and set destination
#    'forwardHuntNoAnswer':
#        {
#        'usePersonalPreferences': 'false',
#        'destination': ( frwdTo ),
#        'callingSearchSpaceName': ( "DEV_" + siteCode +  "_AUC_CSS")
#        },
#    'forwardHuntBusy':
#        {
#        'usePersonalPreferences': 'false',
#        'destination': ( frwdTo ),
#        'callingSearchSpaceName': ( "DEV_" + siteCode +  "_AUC_CSS")
#        }
}

# Execute the addHuntPilot request
try:
    resp = service.addHuntPilot( huntPilot )

except Fault as err:
    print( f'Zeep error: addHuntPilot: { err }' )
    sys.exit( 1 )

print( '\naddHuntPilot response:\n' )
print( resp,'\n' )