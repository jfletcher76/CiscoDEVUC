# Specific to CUCM and supporting tasks
from lxml import etree
from requests import Session
from requests.auth import HTTPBasicAuth
from zeep import Client, Settings, Plugin
from zeep.transports import Transport
from zeep.exceptions import Fault
import sys
import urllib3
import random
# specific to CUPI
import requests
# Edit .env file to specify your user credentials
import os
from dotenv import load_dotenv
load_dotenv()

# Change to true to enable output of request/response headers and XML
DEBUG = False

# The WSDL is a local file in the working directory, see README
# WSDL_FILE = 'schema/AXLAPI.wsdl'
WSDL_FILE = 'C:\Software\CUCM WSDL\AXLAPI.wsdl'

# This class lets you view the incoming and outgoing http headers and XML
class MyLoggingPlugin(Plugin):

    def egress(self, envelope, http_headers, operation, binding_options):

        # Format the request body as pretty printed XML
        xml = etree.tostring(envelope, pretty_print = True, encoding = 'unicode')

        print(f'\nRequest\n-------\nHeaders:\n{http_headers}\n\nBody:\n{xml}')

    def ingress(self, envelope, http_headers, operation):

        # Format the response body as pretty printed XML
        xml = etree.tostring(envelope, pretty_print = True, encoding = 'unicode')

        print(f'\nResponse\n-------\nHeaders:\n{http_headers}\n\nBody:\n{xml}')

# The first step is to create a SOAP client session
session = Session()

# We avoid certificate verification by default
# And disable insecure request warnings to keep the output clear
session.verify = False
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# To enabled SSL cert checking (recommended for production)
# place the CUCM Tomcat cert .pem file in the root of the project
# and uncomment the line below

# session.verify = 'changeme.pem'

# Add Basic Auth credentials
session.auth = HTTPBasicAuth(os.getenv('AXL_USERNAME'), os.getenv('AXL_PASSWORD'))

# Create a Zeep transport and set a reasonable timeout value
transport = Transport(session = session, timeout = 10)

# strict=False is not always necessary, but it allows zeep to parse imperfect XML
settings = Settings(strict = False, xml_huge_tree = True)

# If debug output is requested, add the MyLoggingPlugin callback
plugin = [ MyLoggingPlugin() ] if DEBUG else [ ]

# Create the Zeep client with the specified settings
client = Client(WSDL_FILE, settings = settings, transport = transport,
        plugins = plugin)

# Create the Zeep service binding to AXL at the specified CUCM
service = client.create_service('{http://www.cisco.com/AXLAPIService/}AXLAPIBinding',
                                f'https://{os.getenv("CUCM_ADDRESS")}:8443/axl/')

print('')
print('The script will create the Auction CX Hunt Groups')
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
extensionTRANSPORT=input('Enter TRANSPORT Pilot Extension: ')
#frwdTo=input('Enter RONA number: ')
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
print('TRANSPORT Extension: ' + extensionTRANSPORT)
print('Forward too on no answer: ')
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

groupNames = ["AR", "ARB", "FLEET", "GATEPASS", "INSPECT", "REDEMPTIONS", "SALES", "TITLES_REG", "TRANSPORT"]

# Create Line Group
for x in groupNames:
	lineGroup = {
    	'name': (siteCode + '_CX_' + x + '_LG'),
    	'distributionAlgorithm': 'Broadcast',
    	'rnaReversionTimeOut': '24',
    	'huntAlgorithmNoAnswer': 'Try next member; then, try next group in Hunt List',
    	'huntAlgorithmBusy': 'Try next member; then, try next group in Hunt List',
    	'huntAlgorithmNotAvailable': 'Try next member; then, try next group in Hunt List'
	}

	# Execute the addLineGroup request
	try:
	    resp = service.addLineGroup(lineGroup)

	except Fault as err:
   		print(f'Zeep error: addLineGroup: { err }')
   		sys.exit(1)

print('\naddLineGroup response:\n')
print(resp,'\n')

# Create Hunt List
for x in groupNames:
	huntList = {
    	'name': (siteCode + '_CX_' + x + '_HL'),
    	'description': (siteCode + '_CX_' + x + '_HL'),
    	'callManagerGroupName': (cucmGroup),
    	'routeListEnabled': 'true',
    	'voiceMailUsage': 'true',
    	'members':
        	{
        	'member':
    	        {
	            'lineGroupName': (siteCode + '_CX_' + x + '_LG'),
        	    'selectionOrder': "1"
            	}
        	}
	}

	# Execute the addHuntList request
	try:
	    resp = service.addHuntList(huntList)

	except Fault as err:
   		print(f'Zeep error: addHuntList: { err }')
   		sys.exit(1)

print('\naddHuntList response:\n')
print(resp,'\n')

# Create AR Pilot Number
huntPilot = {
    'pattern': (extensionAR),
    'description': (siteCode + '_CX_AR'),
    'routePartitionName': "Global_DN_PT",
    'patternUrgency': 'false',
    'patternPrecedence': '',
    'provideOutsideDialtone': 'false',
    'huntListName': (siteCode + '_CX_AR_HL'),
    'alertingName': ('""' + siteCode + '_CX_AR_HL""'),
    'asciiAlertingName': (siteCode + '_CX_AR_HL'),
    'maxHuntduration': '32',
    'blockEnable': 'false',
    'useCallingPartyPhoneMask': '',
# if site needs to route calls that are busy or no answer to another destination, need to include the following and set destination
    'forwardHuntNoAnswer':
        {
        'usePersonalPreferences': 'false',
        'destination': ('*' + extensionAR),
        'callingSearchSpaceName': ("DEV_" + siteCode +  "_AUC_CSS")
        },
    'forwardHuntBusy':
        {
        'usePersonalPreferences': 'false',
        'destination': ('*' + extensionAR),
        'callingSearchSpaceName': ("DEV_" + siteCode +  "_AUC_CSS")
        }
}

# Execute the addHuntPilot request
try:
    resp = service.addHuntPilot(huntPilot)

except Fault as err:
    print(f'Zeep error: addHuntPilot: { err }')
    sys.exit(1)

print('\naddHuntPilot response:\n')
print(resp,'\n')

# Create ARB Pilot Number
huntPilot = {
    'pattern': (extensionARB),
    'description': (siteCode + '_CX_ARB'),
    'routePartitionName': "Global_DN_PT",
    'patternUrgency': 'false',
    'patternPrecedence': '',
    'provideOutsideDialtone': 'false',
    'huntListName': (siteCode + '_CX_ARB_HL'),
    'alertingName': ('""' + siteCode + '_CX_ARB_HL""'),
    'asciiAlertingName': (siteCode + '_CX_ARB_HL'),
    'maxHuntduration': '32',
    'blockEnable': 'false',
    'useCallingPartyPhoneMask': '',
# if site needs to route calls that are busy or no answer to another destination, need to include the following and set destination
    'forwardHuntNoAnswer':
        {
        'usePersonalPreferences': 'false',
        'destination': ('*' + extensionARB),
        'callingSearchSpaceName': ("DEV_" + siteCode +  "_AUC_CSS")
        },
    'forwardHuntBusy':
        {
        'usePersonalPreferences': 'false',
        'destination': ('*' + extensionARB),
        'callingSearchSpaceName': ("DEV_" + siteCode +  "_AUC_CSS")
        }
}

# Execute the addHuntPilot request
try:
    resp = service.addHuntPilot(huntPilot)

except Fault as err:
    print(f'Zeep error: addHuntPilot: { err }')
    sys.exit(1)

print('\naddHuntPilot response:\n')
print(resp,'\n')

# Create FLEET Pilot Number
huntPilot = {
    'pattern': (extensionFLEET),
    'description': (siteCode + '_CX_FLEET'),
    'routePartitionName': "Global_DN_PT",
    'patternUrgency': 'false',
    'patternPrecedence': '',
    'provideOutsideDialtone': 'false',
    'huntListName': (siteCode + '_CX_FLEET_HL'),
    'alertingName': ('""' + siteCode + '_CX_FLEET_HL""'),
    'asciiAlertingName': (siteCode + '_CX_FLEET_HL'),
    'maxHuntduration': '32',
    'blockEnable': 'false',
    'useCallingPartyPhoneMask': '',
# if site needs to route calls that are busy or no answer to another destination, need to include the following and set destination
    'forwardHuntNoAnswer':
        {
        'usePersonalPreferences': 'false',
        'destination': ('*' + extensionFLEET),
        'callingSearchSpaceName': ("DEV_" + siteCode +  "_AUC_CSS")
        },
    'forwardHuntBusy':
        {
        'usePersonalPreferences': 'false',
        'destination': ('*' + extensionFLEET),
        'callingSearchSpaceName': ("DEV_" + siteCode +  "_AUC_CSS")
        }
}

# Execute the addHuntPilot request
try:
    resp = service.addHuntPilot(huntPilot)

except Fault as err:
    print(f'Zeep error: addHuntPilot: { err }')
    sys.exit(1)

print('\naddHuntPilot response:\n')
print(resp,'\n')

# Create GATEPASS Pilot Number
huntPilot = {
    'pattern': (extensionGATEPASS),
    'description': (siteCode + '_CX_GATEPASS'),
    'routePartitionName': "Global_DN_PT",
    'patternUrgency': 'false',
    'patternPrecedence': '',
    'provideOutsideDialtone': 'false',
    'huntListName': (siteCode + '_CX_GATEPASS_HL'),
    'alertingName': ('""' + siteCode + '_CX_GATEPASS_HL""'),
    'asciiAlertingName': (siteCode + '_CX_GATEPASS_HL'),
    'maxHuntduration': '32',
    'blockEnable': 'false',
    'useCallingPartyPhoneMask': '',
# if site needs to route calls that are busy or no answer to another destination, need to include the following and set destination
    'forwardHuntNoAnswer':
        {
        'usePersonalPreferences': 'false',
        'destination': ('*' + extensionGATEPASS),
        'callingSearchSpaceName': ("DEV_" + siteCode +  "_AUC_CSS")
        },
    'forwardHuntBusy':
        {
        'usePersonalPreferences': 'false',
        'destination': ('*' + extensionGATEPASS),
        'callingSearchSpaceName': ("DEV_" + siteCode +  "_AUC_CSS")
        }
}

# Execute the addHuntPilot request
try:
    resp = service.addHuntPilot(huntPilot)

except Fault as err:
    print(f'Zeep error: addHuntPilot: { err }')
    sys.exit(1)

print('\naddHuntPilot response:\n')
print(resp,'\n')

# Create INSPECT Pilot Number
huntPilot = {
    'pattern': (extensionINSPECT),
    'description': (siteCode + '_CX_INSPECT'),
    'routePartitionName': "Global_DN_PT",
    'patternUrgency': 'false',
    'patternPrecedence': '',
    'provideOutsideDialtone': 'false',
    'huntListName': (siteCode + '_CX_INSPECT_HL'),
    'alertingName': ('""' + siteCode + '_CX_INSPECT_HL""'),
    'asciiAlertingName': (siteCode + '_CX_INSPECT_HL'),
    'maxHuntduration': '32',
    'blockEnable': 'false',
    'useCallingPartyPhoneMask': '',
# if site needs to route calls that are busy or no answer to another destination, need to include the following and set destination
    'forwardHuntNoAnswer':
        {
        'usePersonalPreferences': 'false',
        'destination': ('*' + extensionINSPECT),
        'callingSearchSpaceName': ("DEV_" + siteCode +  "_AUC_CSS")
        },
    'forwardHuntBusy':
        {
        'usePersonalPreferences': 'false',
        'destination': ('*' + extensionINSPECT),
        'callingSearchSpaceName': ("DEV_" + siteCode +  "_AUC_CSS")
        }
}

# Execute the addHuntPilot request
try:
    resp = service.addHuntPilot(huntPilot)

except Fault as err:
    print(f'Zeep error: addHuntPilot: { err }')
    sys.exit(1)

print('\naddHuntPilot response:\n')
print(resp,'\n')

# Create REDEMPTIONS Pilot Number
huntPilot = {
    'pattern': (extensionREDEMPTIONS),
    'description': (siteCode + '_CX_REDEMPTIONS'),
    'routePartitionName': "Global_DN_PT",
    'patternUrgency': 'false',
    'patternPrecedence': '',
    'provideOutsideDialtone': 'false',
    'huntListName': (siteCode + '_CX_REDEMPTIONS_HL'),
    'alertingName': ('""' + siteCode + '_CX_REDEMPTIONS_HL""'),
    'asciiAlertingName': (siteCode + '_CX_REDEMPTIONS_HL'),
    'maxHuntduration': '32',
    'blockEnable': 'false',
    'useCallingPartyPhoneMask': '',
# if site needs to route calls that are busy or no answer to another destination, need to include the following and set destination
    'forwardHuntNoAnswer':
        {
        'usePersonalPreferences': 'false',
        'destination': ('*' + extensionREDEMPTIONS),
        'callingSearchSpaceName': ("DEV_" + siteCode +  "_AUC_CSS")
        },
    'forwardHuntBusy':
        {
        'usePersonalPreferences': 'false',
        'destination': ('*' + extensionREDEMPTIONS),
        'callingSearchSpaceName': ("DEV_" + siteCode +  "_AUC_CSS")
        }
}

# Execute the addHuntPilot request
try:
    resp = service.addHuntPilot(huntPilot)

except Fault as err:
    print(f'Zeep error: addHuntPilot: { err }')
    sys.exit(1)

print('\naddHuntPilot response:\n')
print(resp,'\n')

# Create SALES Pilot Number
huntPilot = {
    'pattern': (extensionSALES),
    'description': (siteCode + '_CX_SALES'),
    'routePartitionName': "Global_DN_PT",
    'patternUrgency': 'false',
    'patternPrecedence': '',
    'provideOutsideDialtone': 'false',
    'huntListName': (siteCode + '_CX_SALES_HL'),
    'alertingName': ('""' + siteCode + '_CX_SALES_HL""'),
    'asciiAlertingName': (siteCode + '_CX_SALES_HL'),
    'maxHuntduration': '32',
    'blockEnable': 'false',
    'useCallingPartyPhoneMask': '',
# if site needs to route calls that are busy or no answer to another destination, need to include the following and set destination
    'forwardHuntNoAnswer':
        {
        'usePersonalPreferences': 'false',
        'destination': ('*' + extensionSALES),
        'callingSearchSpaceName': ("DEV_" + siteCode +  "_AUC_CSS")
        },
    'forwardHuntBusy':
        {
        'usePersonalPreferences': 'false',
        'destination': ('*' + extensionSALES),
        'callingSearchSpaceName': ("DEV_" + siteCode +  "_AUC_CSS")
        }
}

# Execute the addHuntPilot request
try:
    resp = service.addHuntPilot(huntPilot)

except Fault as err:
    print(f'Zeep error: addHuntPilot: { err }')
    sys.exit(1)

print('\naddHuntPilot response:\n')
print(resp,'\n')

# Create TITLES_REG Pilot Number
huntPilot = {
    'pattern': (extensionTITLES_REG),
    'description': (siteCode + '_CX_TITLES_REG'),
    'routePartitionName': "Global_DN_PT",
    'patternUrgency': 'false',
    'patternPrecedence': '',
    'provideOutsideDialtone': 'false',
    'huntListName': (siteCode + '_CX_TITLES_REG_HL'),
    'alertingName': ('""' + siteCode + '_CX_TITLES_REG_HL""'),
    'asciiAlertingName': (siteCode + '_CX_TITLES_REG_HL'),
    'maxHuntduration': '32',
    'blockEnable': 'false',
    'useCallingPartyPhoneMask': '',
# if site needs to route calls that are busy or no answer to another destination, need to include the following and set destination
    'forwardHuntNoAnswer':
        {
        'usePersonalPreferences': 'false',
        'destination': ('*' + extensionTITLES_REG),
        'callingSearchSpaceName': ("DEV_" + siteCode +  "_AUC_CSS")
        },
    'forwardHuntBusy':
        {
        'usePersonalPreferences': 'false',
        'destination': ('*' + extensionTITLES_REG),
        'callingSearchSpaceName': ("DEV_" + siteCode +  "_AUC_CSS")
        }
}

# Execute the addHuntPilot request
try:
    resp = service.addHuntPilot(huntPilot)

except Fault as err:
    print(f'Zeep error: addHuntPilot: { err }')
    sys.exit(1)

print('\naddHuntPilot response:\n')
print(resp,'\n')

# Create TRANSPORT Pilot Number
huntPilot = {
    'pattern': (extensionTRANSPORT),
    'description': (siteCode + '_CX_TRANSPORT_REG'),
    'routePartitionName': "Global_DN_PT",
    'patternUrgency': 'false',
    'patternPrecedence': '',
    'provideOutsideDialtone': 'false',
    'huntListName': (siteCode + '_CX_TRANSPORT_REG_HL'),
    'alertingName': ('""' + siteCode + '_CX_TRANSPORT_REG_HL""'),
    'asciiAlertingName': (siteCode + '_CX_TRANSPORT_REG_HL'),
    'maxHuntduration': '32',
    'blockEnable': 'false',
    'useCallingPartyPhoneMask': '',
# if site needs to route calls that are busy or no answer to another destination, need to include the following and set destination
    'forwardHuntNoAnswer':
        {
        'usePersonalPreferences': 'false',
        'destination': ('*' + extensionTRANSPORT),
        'callingSearchSpaceName': ("DEV_" + siteCode +  "_AUC_CSS")
        },
    'forwardHuntBusy':
        {
        'usePersonalPreferences': 'false',
        'destination': ('*' + extensionTRANSPORT),
        'callingSearchSpaceName': ("DEV_" + siteCode +  "_AUC_CSS")
        }
}

# Execute the addHuntPilot request
try:
    resp = service.addHuntPilot(huntPilot)

except Fault as err:
    print(f'Zeep error: addHuntPilot: { err }')
    sys.exit(1)

print('\naddHuntPilot response:\n')
print(resp,'\n')

# Create a new Unity user
req = {
    'Alias': (siteCode + '_AR'),
    'FirstName': (siteCode + '_AR'),
    'LastName': ('Voicemail'),
    'DtmfAccessId': (extensionAR),
    'DisplayName': (siteCode + '_AR')
}

try:
    resp = requests.post(
        f'https://{ os.getenv("CUC_ADDRESS") }/vmrest/users?templateAlias=User_Template_NO_OFFICE365',
        auth=HTTPBasicAuth(os.getenv('CUC_USER'), os.getenv('CUC_PASSWORD')),
        json = req,
        verify = False
       )

    # Raise an exception if a non-200/201 HTTP response received
    resp.raise_for_status()
    
    print('')
    print('Account Successfully Created: ', resp)
    print('')
    
except Exception as err:
    print('')
    print(f'Request error: POST ../users: { err }')
    print('')
    print('Account Creation Error: ', resp)
    print('')
    sys.exit(1)

# Create a new Unity user
req = {
    'Alias': (siteCode + '_ARB'),
    'FirstName': (siteCode + '_ARB'),
    'LastName': ('Voicemail'),
    'DtmfAccessId': (extensionARB),
    'DisplayName': (siteCode + '_ARB')
}

try:
    resp = requests.post(
        f'https://{ os.getenv("CUC_ADDRESS") }/vmrest/users?templateAlias=User_Template_NO_OFFICE365',
        auth=HTTPBasicAuth(os.getenv('CUC_USER'), os.getenv('CUC_PASSWORD')),
        json = req,
        verify = False
       )

    # Raise an exception if a non-200/201 HTTP response received
    resp.raise_for_status()
    
    print('')
    print('Account Successfully Created: ', resp)
    print('')
    
except Exception as err:
    print('')
    print(f'Request error: POST ../users: { err }')
    print('')
    print('Account Creation Error: ', resp)
    print('')
    sys.exit(1)

# Create a new Unity user
req = {
    'Alias': (siteCode + '_FLEET'),
    'FirstName': (siteCode + '_FLEET'),
    'LastName': ('Voicemail'),
    'DtmfAccessId': (extensionFLEET),
    'DisplayName': (siteCode + '_FLEET')
}

try:
    resp = requests.post(
        f'https://{ os.getenv("CUC_ADDRESS") }/vmrest/users?templateAlias=User_Template_NO_OFFICE365',
        auth=HTTPBasicAuth(os.getenv('CUC_USER'), os.getenv('CUC_PASSWORD')),
        json = req,
        verify = False
       )

    # Raise an exception if a non-200/201 HTTP response received
    resp.raise_for_status()
    
    print('')
    print('Account Successfully Created: ', resp)
    print('')
    
except Exception as err:
    print('')
    print(f'Request error: POST ../users: { err }')
    print('')
    print('Account Creation Error: ', resp)
    print('')
    sys.exit(1)

# Create a new Unity user
req = {
    'Alias': (siteCode + '_GATEPASS'),
    'FirstName': (siteCode + '_GATEPASS'),
    'LastName': ('Voicemail'),
    'DtmfAccessId': (extensionGATEPASS),
    'DisplayName': (siteCode + '_GATEPASS')
}

try:
    resp = requests.post(
        f'https://{ os.getenv("CUC_ADDRESS") }/vmrest/users?templateAlias=User_Template_NO_OFFICE365',
        auth=HTTPBasicAuth(os.getenv('CUC_USER'), os.getenv('CUC_PASSWORD')),
        json = req,
        verify = False
       )

    # Raise an exception if a non-200/201 HTTP response received
    resp.raise_for_status()
    
    print('')
    print('Account Successfully Created: ', resp)
    print('')
    
except Exception as err:
    print('')
    print(f'Request error: POST ../users: { err }')
    print('')
    print('Account Creation Error: ', resp)
    print('')
    sys.exit(1)

# Create a new Unity user
req = {
    'Alias': (siteCode + '_INSPECT'),
    'FirstName': (siteCode + '_INSPECT'),
    'LastName': ('Voicemail'),
    'DtmfAccessId': (extensionINSPECT),
    'DisplayName': (siteCode + '_INSPECT')
}

try:
    resp = requests.post(
        f'https://{ os.getenv("CUC_ADDRESS") }/vmrest/users?templateAlias=User_Template_NO_OFFICE365',
        auth=HTTPBasicAuth(os.getenv('CUC_USER'), os.getenv('CUC_PASSWORD')),
        json = req,
        verify = False
       )

    # Raise an exception if a non-200/201 HTTP response received
    resp.raise_for_status()
    
    print('')
    print('Account Successfully Created: ', resp)
    print('')
    
except Exception as err:
    print('')
    print(f'Request error: POST ../users: { err }')
    print('')
    print('Account Creation Error: ', resp)
    print('')
    sys.exit(1)

# Create a new Unity user
req = {
    'Alias': (siteCode + '_REDEMPTIONS'),
    'FirstName': (siteCode + '_REDEMPTIONS'),
    'LastName': ('Voicemail'),
    'DtmfAccessId': (extensionREDEMPTIONS),
    'DisplayName': (siteCode + '_REDEMPTIONS')
}

try:
    resp = requests.post(
        f'https://{ os.getenv("CUC_ADDRESS") }/vmrest/users?templateAlias=User_Template_NO_OFFICE365',
        auth=HTTPBasicAuth(os.getenv('CUC_USER'), os.getenv('CUC_PASSWORD')),
        json = req,
        verify = False
       )

    # Raise an exception if a non-200/201 HTTP response received
    resp.raise_for_status()
    
    print('')
    print('Account Successfully Created: ', resp)
    print('')
    
except Exception as err:
    print('')
    print(f'Request error: POST ../users: { err }')
    print('')
    print('Account Creation Error: ', resp)
    print('')
    sys.exit(1)

# Create a new Unity user
req = {
    'Alias': (siteCode + '_SALES'),
    'FirstName': (siteCode + '_SALES'),
    'LastName': ('Voicemail'),
    'DtmfAccessId': (extensionSALES),
    'DisplayName': (siteCode + '_SALES')
}

try:
    resp = requests.post(
        f'https://{ os.getenv("CUC_ADDRESS") }/vmrest/users?templateAlias=User_Template_NO_OFFICE365',
        auth=HTTPBasicAuth(os.getenv('CUC_USER'), os.getenv('CUC_PASSWORD')),
        json = req,
        verify = False
       )

    # Raise an exception if a non-200/201 HTTP response received
    resp.raise_for_status()
    
    print('')
    print('Account Successfully Created: ', resp)
    print('')
    
except Exception as err:
    print('')
    print(f'Request error: POST ../users: { err }')
    print('')
    print('Account Creation Error: ', resp)
    print('')
    sys.exit(1)

# Create a new Unity user
req = {
    'Alias': (siteCode + '_TITLES_REG'),
    'FirstName': (siteCode + '_TITLES_REG'),
    'LastName': ('Voicemail'),
    'DtmfAccessId': (extensionTITLES_REG),
    'DisplayName': (siteCode + '_TITLES_REG')
}

try:
    resp = requests.post(
        f'https://{ os.getenv("CUC_ADDRESS") }/vmrest/users?templateAlias=User_Template_NO_OFFICE365',
        auth=HTTPBasicAuth(os.getenv('CUC_USER'), os.getenv('CUC_PASSWORD')),
        json = req,
        verify = False
       )

    # Raise an exception if a non-200/201 HTTP response received
    resp.raise_for_status()
    
    print('')
    print('Account Successfully Created: ', resp)
    print('')
    
except Exception as err:
    print('')
    print(f'Request error: POST ../users: { err }')
    print('')
    print('Account Creation Error: ', resp)
    print('')
    sys.exit(1)

# Create a new Unity user
req = {
    'Alias': (siteCode + '_TRANSPORT'),
    'FirstName': (siteCode + '_TRANSPORT'),
    'LastName': ('Voicemail'),
    'DtmfAccessId': (extensionTRANSPORT),
    'DisplayName': (siteCode + '_TRANSPORT')
}

try:
    resp = requests.post(
        f'https://{ os.getenv("CUC_ADDRESS") }/vmrest/users?templateAlias=User_Template_NO_OFFICE365',
        auth=HTTPBasicAuth(os.getenv('CUC_USER'), os.getenv('CUC_PASSWORD')),
        json = req,
        verify = False
       )

    # Raise an exception if a non-200/201 HTTP response received
    resp.raise_for_status()
    
    print('')
    print('Account Successfully Created: ', resp)
    print('')
    
except Exception as err:
    print('')
    print(f'Request error: POST ../users: { err }')
    print('')
    print('Account Creation Error: ', resp)
    print('')
    sys.exit(1)