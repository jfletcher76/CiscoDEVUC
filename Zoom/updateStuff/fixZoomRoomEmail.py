#THIS SCRIPT IS UDNER DEVELOPMENT.  DO NOT USE

import os
from time import sleep
import requests
from dotenv import load_dotenv
load_dotenv()

key = (f'Bearer {os.getenv("ZOOM_TOKEN")}')
headers = {'Authorization': key}

zoomRoomName=input('\nEnter Zoom Room Name: ')
newRoomEmail=input('Enter new calendar email for room: ')
print('')

# Gets the zoom room ID based off the name
res = requests.post(
    'https://api.zoom.us/v2/rooms/zrlist',
    headers=headers,
    json={"method": "list", "params": {"zr_name": zoomRoomName}}
)

res.raise_for_status()
# print(res.json())
zoomRoomId=res.json()['result']['data'][0]['zr_id']

print(f'\nZoom room name: {zoomRoomName}')
print(f'ZoomRoomID: {zoomRoomId}')

url = f"https://api.zoom.us/v2/rooms/{zoomRoomId}"
response = requests.request("GET", url, headers=headers)
json_data = response.json()
print('\n', json_data)
#print(f'Calendar Resource ID: ' + json_data['basic'].get('calendar_resource_id'))
try:
    url = f"https://api.zoom.us/v2/rooms/calendar/services/{accountID}/resources/{json_data['basic']['calendar_resource_id']}"
    response = requests.request("GET", url, headers=headers)
    json_data2 = response.json()
    # print('\n', json_data2)
    print('Current zoom room calendar resource email: ' + json_data2['calendar_resource_email'])
    print(f'Room will change to this email: {newRoomEmail}')

except:
    print('Current zoom room calendar resource email: None')

req = {
    'basic': {
        'calendar_resource_id': newRoomEmail
    }
}

try:
    # Clear calendar resource
    # resp = requests.patch( 
    #     f"https://api.zoom.us/v2/rooms/{zoomRoomId}",
    #     headers=headers,
    #     json = {
    #         'basic': {
    #             "calendar_resource_id": ""
    #         }
    #     }
    # )
    # Assign new calendar resource
    resp = requests.patch( 
        f"https://api.zoom.us/v2/rooms/{zoomRoomId}",
        headers=headers,
        json = req
    )
    # print(resp.content)
    print(f'Successfully updated {zoomRoomName}', resp)
except:
    print(f'\nFailed to update {zoomRoomName}', resp)

print('\nJob Complete')
