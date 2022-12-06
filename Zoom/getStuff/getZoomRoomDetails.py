import os
import requests
from dotenv import load_dotenv
load_dotenv()

key = (f'Bearer {os.getenv("ZOOM_TOKEN")}')
headers = {'Authorization': key}

zoomRoomName=input('\nEnter Zoom Room Name: ')
print('')

res = requests.post(
    'https://api.zoom.us/v2/rooms/zrlist',
    headers=headers,
    json={"method": "list", "params": {"zr_name": zoomRoomName}}
)

res.raise_for_status()
print(res.json())
zoomRoomId=res.json()['result']['data'][0]['zr_id']

print(f'\nZoom room name: {zoomRoomName}')
print(f'ZoomRoomID: {zoomRoomId}')

url = f"https://api.zoom.us/v2/rooms/{zoomRoomId}"
response = requests.request("GET", url, headers=headers)
json_data = response.json()
print('\n', json_data)

url = f"https://api.zoom.us/v2/rooms/{zoomRoomId}/device_profiles"
response = requests.request("GET", url, headers=headers)
json_data = response.json()
print('\n', json_data)
