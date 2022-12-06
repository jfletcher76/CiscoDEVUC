import os
import requests
from dotenv import load_dotenv
load_dotenv()

key = (f'Bearer {os.getenv("ZOOM_TOKEN")}')
headers = {'Authorization': key}

res = requests.post(
    'https://api.zoom.us/v2/rooms/zrlist',
    headers=headers,
    json={"method": "list", "params": {f"zr_name": {ZOOM_ROOM_NAME}}}
)

res.raise_for_status()
print(res.json())

zoomRoomId=res.json()['result']['data'][0]['zr_id']

url = f"https://api.zoom.us/v2/rooms/{zoomRoomId}"
response = requests.request("GET", url, headers=headers)
json_data = response.json()
print('\n', json_data)


url = f"https://api.zoom.us/v2/rooms/calendar/services/{zoom_room_id}/{json_data['basic']['calendar_resource_id']}"
response = requests.request("GET", url, headers=headers)
json_data2 = response.json()
print('\n', json_data2)

req = {
    'calendar_resource_email': f'{calendar_email}',
}

try:
    resp = requests.patch( 
        f"https://api.zoom.us/v2/rooms/{zoomRoomId}",
        headers=headers,
        json = req
        )
    # Raise an exception if a non-200/201 HTTP response received
    print('\nRoom Successfully updated to EMail Here', resp)
except:
    print('\nRoom failed to change', resp)
    resp.raise_for_status()