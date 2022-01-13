from lxml import etree
from requests import Session
from requests.auth import HTTPBasicAuth
from zeep import Client, Settings, Plugin
from zeep.transports import Transport
from zeep.exceptions import Fault
import sys
import urllib3
import random

# Needed for pop up menu
import PySimpleGUI as sg

# Edit .env file to specify your Webex site/user details
import os
from dotenv import load_dotenv
load_dotenv()

# Change to true to enable output of request/response headers and XML
DEBUG = False

# The WSDL is a local file in the working directory, see README
# WSDL_FILE = 'schema/AXLAPI.wsdl'
WSDL_FILE = 'C:\CUCM WSDL\AXLAPI.wsdl' # add your wsdl here, example to the left, can also use a network share


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

# Gather User Information for creation
sg.theme('DarkBlue12')
layout = [
    [sg.Text('Please enter the below info')],
    [sg.Text('Enter Site Code', size =(20, 1)), sg.InputText()],
    [sg.Text('')],
    [sg.Text('Location Type: REM, HQ - use all caps please')],
    [sg.Text('Enter Location Type', size =(20, 1)), sg.InputText()],
    [sg.Text('')],
    [sg.Text('Select Location Time Zone')],
    [sg.Combo(values=('EST-EDT', 'CST-CDT', 'MST-MDT', 'PST-PDT', 'ADT-STJ', 'AKST-AKDT', 'AST-ADT'), default_value='', readonly=True, k='-COMBO1-')],
    [sg.Text('')],
    [sg.Text('Enter 4 digit translations pattern (with X\'s all caps)')],
    [sg.Text('Enter Translation', size =(20, 1)), sg.InputText()],
    [sg.Text('')],
    [sg.Text('Enter site 4 digit prefix', size =(20, 1)), sg.InputText()],
    [sg.Text('')],
    [sg.Text('Enter Site Main Line', size =(20, 1)), sg.InputText()],
    [sg.Text('')],
    [sg.Submit(), sg.Cancel()]
]

window = sg.Window('Add site to CUCM', layout)

while True:
    event, values = window.read()
    if event=="Cancel" or event==sg.WIN_CLOSED:
        break
    elif event=='Submit' and values['-COMBO1-'] == '' or values[0] == '' or values[1] == '' or values[2] == '' or values[3] == '' or values[4] == '':
        sg.popup('', 'Invalid entry try again', '')
    elif event=='Submit':
        siteCode=values[0]
        locationType=values[1]        
        timeZone=values['-COMBO1-']
        siteXlate=values[2]
        siteXlatePrefix=values[3]
        siteMainLine=values[4]
        window.close()

globalName=(siteCode + '_' + locationType)

if locationType.upper() == 'REM':
    softKey=('RemoteLocation Softkey')
else:
    softKey=('HQ User with DND')

# This section will print out a small verification step to allow you to double check your settings
# To continue you must type VERIFY exactly in all caps as a way to not accidentally start the script if you see an error

# print('----------------------------------------------------------')
# print('--------------------Verify Settings-----------------------')
# print('----------------------------------------------------------')
# print('')
# print('Site Global Name: ' + globalName)
# print('Device Pool: ' + globalName + '_DP')
# print('Site Time Zone: ' + timeZone)
# print('Example Partition: ' + globalName + '_LD_PT')
# print('Example CSS: ' + globalName + '_LD_CSS')
# print('Site Main Line Route Point: ' + siteMainLine)
# print('Site 4 Digit Xlate: ' + siteXlate)
# print('Site 4 Digit Xlate Prefix: ' + siteXlatePrefix)
# print('Site 11 Digit Extension: ' + siteXlatePrefix + siteXlate)
# print('Location Softkey Template: ' + softKey)
# print('')
# verifySettings=input('If settings look correct type VERIFY to continue to build location, otherwise press enter to exit: ')

# if verifySettings != 'VERIFY' :
#     print('Script Aborting')
#     exit()
# else:
#     print('Script will run with above settings')

# This logic will try to balance the configuration of multiple locations across two active CMs.  If you only have one
# modify the script to accomodate
rando=random.randint(1,1000)
iRemainder = (rando % 2)
if iRemainder == 0:
    cucmGroup = 'CUCM_Group_1'
else:
    cucmGroup = 'CUCM_Group_2'

# Create Physical Location
physLoc = {
    'name': ( globalName + '_PHYL' ),
    'description': ( globalName + ' Physical Location')
    }

# Execute the addPhysicalLocation request
try:
    resp = service.addPhysicalLocation( physLoc )

except Fault as err:
    print( f'Zeep error: addPhysicalLocation: { err }' )
    sys.exit( 1 )

print( '\naddPhysicalLocation response:\n' )
print( resp,'\n' )

# Create Location
siteLoc = {
    'name': ( globalName + '_LOC' ),
    'withinAudioBandwidth': '0',
    'withinVideoBandwidth': '0',
    'withinImmersiveKbits': '0',
    'betweenLocations':
    {
        'betweenLocation':
        {
            'locationName': 'Hub_None',
            'weight': '50',
            'audioBandwidth': '0',
            'videoBandwidth': '384',
            'immersiveBandwidth': '384'
        }
    }
}

# Execute the addLocation request
try:
    resp = service.addLocation( siteLoc )

except Fault as err:
    print( f'Zeep error: addLocation: { err }' )
    sys.exit( 1 )

print( '\naddLocation response:\n' )
print( resp,'\n' )

# Create Site MRGL
siteMRGL = {
    'name': ( globalName + '_MRGL' ),
    'members':
    {
        'member':
        {
            'mediaResourceGroupName': 'CUCM_SW_MRG',
            'order': '1'
        }
    }
}

# Execute the addMRGL request
try:
    resp = service.addMediaResourceList( siteMRGL )

except Fault as err:
    print( f'Zeep error: addMediaResourceList: { err }' )
    sys.exit( 1 )

print( '\naddMediaResourceList response:\n' )
print( resp,'\n' )

# Create devicePool
siteDP = {
    'name': ( globalName + '_DP' ),
    'dateTimeSettingName': (timeZone),
    'callManagerGroupName': ( cucmGroup ),
    'mediaResourceListName': ( globalName + '_MRGL'),
    'regionName': 'G711_REG',
    'networkLocale': 'United States',
    'connectionMonitorDuration': '120',
    'locationName': ( globalName + '_LOC' ),
    'physicalLocationName': ( globalName + '_PHYL' ),
    'srstName': 'Disable'
}

# Execute the addDP request
try:
    resp = service.addDevicePool( siteDP )

except Fault as err:
    print( f'Zeep error: addDevicePool: { err }' )
    sys.exit( 1 )

print( '\naddDevicePool response:\n' )
print( resp,'\n' )

# This is where we create the common device config
# This is mostly necessary if we are going to set a custom MOH or SoftKey at the device level for a specific site

# Create CommonDeviceConfig
siteCDC = {
    'name': ( globalName + '_CDC' ),
    'softkeyTemplateName': (softKey),
    'networkHoldMohAudioSourceId': '1',
    'userHoldMohAudioSourceId': '1',
    'userLocale': 'English United States',
    'ipAddressingMode': 'IPv4 and IPv6',
    'ipAddressingModePreferenceControl': 'Use System Default'
}

# Execute the addCommonDeviceConfig request
try:
    resp = service.addCommonDeviceConfig( siteCDC )

except Fault as err:
    print( f'Zeep error: addCommonDeviceConfig: { err }' )
    sys.exit( 1 )

print( '\naddCommonDeviceConfig response:\n' )
print( resp,'\n' )

# Create commonPhoneConfig siteCode_locationType Common Phone Profile
commonPhoneConfig = {
    'name': ( globalName + ' Common Phone Profile' ),
    'description': ( globalName + ' Common Phone Profile' ),
    'dndOption': 'Ringer Off',
    'dndAlertingType': 'Beep Only',
    'alwaysUsePrimeLine': 'Default',
    'alwaysUsePrimeLineForVoiceMessage': 'Default',
    }

# Create an Element object from scratch with tag 'lineMode' and text '1'
lineMode = etree.Element( 'lineMode' )
lineMode.text = '1'

# Append each top-level element to an array
vendorConfig = []
vendorConfig.append( lineMode )

# Create a Zeep xsd type object of type XVendorConfig from the client object
xvcType = client.get_type( 'ns0:XVendorConfig' )

# Use the XVendorConfig type object to create a vendorConfig object
#   using the array of vendorConfig elements from above, and set as
#   phone.vendorConfig
commonPhoneConfig[ 'vendorConfig' ] = xvcType( vendorConfig )

# Execute the addCommonPhoneConfig request
try:
    resp = service.addCommonPhoneConfig( commonPhoneConfig )

except Fault as err:
    print( f'Zeep error: addCommonPhoneConfig: { err }' )
    sys.exit( 1 )

print( '\naddCommonPhoneConfig response:\n' )
print( resp,'\n' )

# This part of script requires a separate request for each Partition created
# There should be 9 Partitions (911, INTL, LD, LOCAL, PAGING, TOLLFREE, XLATE, PARK and NULL)
# Modify this list if you want different partitions, the script will only create what you have in the list using the for x loop

cucmPartitions = ['911', 'INTL', 'LD', 'LOCAL', 'PAGING', 'TOLLFREE', 'XLATE', 'NULL', 'PARK']

for x in cucmPartitions:
    routePartition = {
    'name': ( f'{globalName}_{x}_PT' ),
    'description': ( f'{globalName}_{x}_PT' ),
    'useOriginatingDeviceTimeZone': 'true'
}

    # Execute the addRoutePartition request
    try:
        resp = service.addRoutePartition( routePartition )

    except Fault as err:
        print( f'Zeep error: addRoutePartition: { err }' )
        sys.exit( 1 )

    print( '\naddRoutePartition response:\n' )
    print( resp,'\n' )

# This part adds the DEV CSS and associates all the PTs for the location to it
# Create DEV_CSS PT
callingSearchSpace = {
    'name': ( 'DEV_' + globalName + '_CSS' ),
    'description': ( 'DEV_' + globalName + '_CSS' ),
    'useOriginatingDeviceTimeZone': 'true',
    'members': { 
        'member': [ ] 
    }
} 

callingSearchSpace[ 'members' ][ 'member' ].append(
    {
            'routePartitionName': ( globalName + '_911_PT' ),
            'index': '1'
    }
)

callingSearchSpace[ 'members' ][ 'member' ].append(
    {
            'routePartitionName': ( globalName + '_XLATE_PT' ),
            'index': '2'
    }
)

callingSearchSpace[ 'members' ][ 'member' ].append(
    {
            'routePartitionName': 'GLOBAL_XLATE_PT',
            'index': '3'
    }
)

callingSearchSpace[ 'members' ][ 'member' ].append(
    {
            'routePartitionName': 'GLOBAL_DN_PT',
            'index': '4'
    }
)

callingSearchSpace[ 'members' ][ 'member' ].append(
    {
            'routePartitionName': ( globalName + '_LOCAL_PT' ),
            'index': '5'
    }
)

callingSearchSpace[ 'members' ][ 'member' ].append(
    {
            'routePartitionName': ( globalName + '_LD_PT' ),
            'index': '6'
    }
)

callingSearchSpace[ 'members' ][ 'member' ].append(
    {
            'routePartitionName': ( globalName + '_INTL_PT' ),
            'index': '7'
    }
)

callingSearchSpace[ 'members' ][ 'member' ].append(
    {
            'routePartitionName': ( globalName + '_TOLLFREE_PT' ),
            'index': '8'
    }
)

callingSearchSpace[ 'members' ][ 'member' ].append(
    {
            'routePartitionName': ( globalName + '_PAGING_PT' ),
            'index': '9'
    }
)

callingSearchSpace[ 'members' ][ 'member' ].append(
    {
            'routePartitionName': ( globalName + '_PARK_PT' ),
            'index': '10'
    }
)

# Execute the addCss request
try:
    resp = service.addCss( callingSearchSpace )

except Fault as err:
    print( f'Zeep error: addCss: { err }' )
    sys.exit( 1 )

print( '\naddCss response:\n' )
print( resp,'\n' )

# This creates the sites INTERNAL only CSS
# Create INTERNAL_CSS PT
callingSearchSpace = {
    'name': ( globalName + '_INTERNAL_CSS' ),
    'description': ( globalName + '_INTERNAL_CSS' ),
    'useOriginatingDeviceTimeZone': 'true',
    'members': { 
        'member': [ ] 
    }
} 

callingSearchSpace[ 'members' ][ 'member' ].append(
    {
            'routePartitionName': 'BLOCK_TOLL_FRAUD_PT',
            'index': '1'
    }
)

callingSearchSpace[ 'members' ][ 'member' ].append(
    {
            'routePartitionName': 'BLOCK_TOLL_FREE_PT',
            'index': '2'
    }
)

callingSearchSpace[ 'members' ][ 'member' ].append(
    {
            'routePartitionName': 'BLOCK_INTL_PT',
            'index': '3'
    }
)

callingSearchSpace[ 'members' ][ 'member' ].append(
    {
            'routePartitionName': 'BLOCK_LD_PT',
            'index': '4'
    }
)

# Execute the addCss request
try:
    resp = service.addCss( callingSearchSpace )

except Fault as err:
    print( f'Zeep error: addCss: { err }' )
    sys.exit( 1 )

print( '\naddCss response:\n' )
print( resp,'\n' )

# This creates the sites LD only CSS
# Create LD_CSS PT
callingSearchSpace = {
    'name': ( globalName + '_LD_CSS' ),
    'description': ( globalName + '_LD_CSS' ),
    'useOriginatingDeviceTimeZone': 'true',
    'members': { 
        'member': [ ] 
    }
} 

callingSearchSpace[ 'members' ][ 'member' ].append(
    {
            'routePartitionName': 'BLOCK_TOLL_FRAUD_PT',
            'index': '1'
    }
)

callingSearchSpace[ 'members' ][ 'member' ].append(
    {
            'routePartitionName': 'BLOCK_INTL_PT',
            'index': '2'
    }
)

# Execute the addCss request
try:
    resp = service.addCss( callingSearchSpace )

except Fault as err:
    print( f'Zeep error: addCss: { err }' )
    sys.exit( 1 )

print( '\naddCss response:\n' )
print( resp,'\n' )

# This creates the sites INTL only CSS
# Create INTL_CSS PT
callingSearchSpace = {
    'name': ( globalName + '_INTL_CSS' ),
    'description': ( globalName + '_INTL_CSS' ),
    'useOriginatingDeviceTimeZone': 'true',
    'members': { 
        'member': [ ] 
    }
} 

callingSearchSpace[ 'members' ][ 'member' ].append(
    {
            'routePartitionName': 'BLOCK_TOLL_FRAUD_PT',
            'index': '1'
    }
)

# Execute the addCss request
try:
    resp = service.addCss( callingSearchSpace )

except Fault as err:
    print( f'Zeep error: addCss: { err }' )
    sys.exit( 1 )

print( '\naddCss response:\n' )
print( resp,'\n' )

# These next steps create all the route patterns for the site
# Loop will create all patterns from the list that follows and if you need to add new patterns, just add it to the list

cucmPatterns=[['1[2-9]XX[2-9]XXXXXX', ' 11 Digit Route Pattern', globalName + '_LD_PT'], 
    ['011.!', ' International', globalName + '_INTL_PT'],
    ['011.1#', ' International', globalName + '_INTL_PT'],
    ['1800XXXXXXX', ' Toll Free', globalName + '_TOLLFREE_PT'],
    ['1833XXXXXXX', ' Toll Free', globalName + '_TOLLFREE_PT'],
    ['1844XXXXXXX', ' Toll Free', globalName + '_TOLLFREE_PT'],
    ['1855XXXXXXX', ' Toll Free', globalName + '_TOLLFREE_PT'],
    ['1866XXXXXXX', ' Toll Free', globalName + '_TOLLFREE_PT'],
    ['1877XXXXXXX', ' Toll Free', globalName + '_TOLLFREE_PT'],
    ['1888XXXXXXX', ' Toll Free', globalName + '_TOLLFREE_PT']
    ]

for x in cucmPatterns:
    routePattern = {
        'pattern': (x[0]),
        'description': (globalName + x[1]),
        'routePartitionName': (x[2]),
        'blockEnable': 'false',
        'networkLocation': 'OffNet',
        'prefixDigitsOut': '+',
        'patternPrecedence': 'Default',
        'useCallingPartyPhoneMask': '',
        'destination':
            {
            'routeListName': 'SBC_RL'
            }
        }
    
    # Execute the addRoutePattern request
    try:
        resp = service.addRoutePattern( routePattern )

    except Fault as err:
        print( f'Zeep error: addRoutePattern: { err }' )
        sys.exit( 1 )

    print( '\naddRoutePattern response:\n' )
    print( resp,'\n' )

# This part adds the sites 4 digit translation patterns for internal 4 digit dialing

# Create 4 digit xlate to phones 11 digit lines
transPattern = {
    'pattern': (siteXlate),
    'description': ( globalName + ' 4 digit xlate'),
    'routePartitionName': ( globalName + '_XLATE_PT'),
    'patternUrgency': 'True',
    'prefixDigitsOut': (siteXlatePrefix),
    'usage': 'Translation',
    'callingSearchSpaceName': 'CUCM_DN_CSS'
}

# Execute the addTransPattern request
try:
    resp = service.addTransPattern( transPattern )

except Fault as err:
    print( f'Zeep error: addTransPattern: { err }' )
    sys.exit( 1 )

print( '\naddTransPattern response:\n' )
print( resp,'\n' )

# Create 4 digit xlate to VM
transPattern = {
    'pattern': ('*.' + siteXlate),
    'description': ( globalName + ' 4 digit to VM xlate'),
    'routePartitionName': ( globalName + '_XLATE_PT'),
    'patternUrgency': 'True',
    'prefixDigitsOut': ( '*' + siteXlatePrefix),
    'usage': 'Translation',
    'callingSearchSpaceName': 'CUCM_DN_CSS',
    'digitDiscardInstructionName': 'PreDot'
}

# Execute the addTransPattern request
try:
    resp = service.addTransPattern( transPattern )

except Fault as err:
    print( f'Zeep error: addTransPattern: { err }' )
    sys.exit( 1 )

print( '\naddTransPattern response:\n' )
print( resp,'\n' )

# This process adds a line, then adds a CTI route point and associates the line to the route point

# Create a RP Line
line = {
    'pattern': (siteMainLine),
    'description': ( globalName + ' Main Line'),
    'alertingName': ( globalName + ' Main Line'),
    'asciiAlertingName': ( globalName + ' Main Line'),
    'usage': 'Device',
    'routePartitionName': ( globalName + '_NULL_PT' ),
    'voiceMailProfileName': 'CUCM_VM',
    'shareLineAppearanceCssName': ( 'CUCM_DN_CSS' ),
    'callForwardAll':
        {
        'forwardToVoiceMail': 'True',
        'callingSearchSpaceName': ('DEV_CUCM_HQ_CSS'),
        'secondaryCallingSearchSpaceName': ('DEV_CUCM_HQ_CSS')
        }
}

# Execute the addLine request
try:
    resp = service.addLine( line )

except Fault as err:
    print( f'Zeep error: addLine: { err }' )
    sys.exit( 1 )

print( '\naddLine response:\n' )
print( resp,'\n' )

# Create and Associate CTI to Line Above
ctiRoute = {
    'name': ( globalName + '_RP'),
    'description': ( globalName + '_RP'),
    'product': 'CTI Route Point',
    'class': 'CTI Route Point',
    'protocol': 'SCCP',
    'protocolSide': 'User',
    'callingSearchSpaceName': 'DEV_CUCM_HQ_CSS', # modify to fit your org
    'devicePoolName': 'CORE-SVC_DP', # modify to fit your org
    'commonDeviceConfigName': 'CUCM_HQ_CDC', # modify to fit your org
    'locationName': 'CUCM_HQ_LOC', # modify to fit your org
    'mediaResourceListName': 'CLUSTER_MRGL', # modify to fit your org
    'useTrustedRelayPoint': 'Default',
    'lines': 
    {
        'line':
        {
            'index': '1',
            'label': ( globalName + ' Main Line'),
            'display': ( globalName + ' Main Line'),
            'displayAscii': ( globalName + ' Main Line'),
            'maxNumCalls': '5000',
            'busyTrigger': '4500',
            'dirn':
            {
                'pattern': ( siteMainLine ),
                'routePartitionName': ( globalName + '_NULL_PT' )
            }
        }
    }
}

# Execute the addCtiRoutePoint request
try:
    resp = service.addCtiRoutePoint( ctiRoute )

except Fault as err:
    print( f'Zeep error: addCtiRoutePoint: { err }' )
    sys.exit( 1 )

print( '\naddCtiRoutePoint response:\n' )
print( resp,'\n' )