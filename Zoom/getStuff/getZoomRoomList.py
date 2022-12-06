import os
import requests
from dotenv import load_dotenv
load_dotenv()

key = (f'Bearer {os.getenv("ZOOM_TOKEN")}')
# key = (f'Bearer {os.getenv("ZOOM_DEV_TOKEN")}')
headers = {'Authorization': key}

url = f"https://api.zoom.us/v2/rooms"

response = requests.request("GET", url, headers=headers)

print(response._content)

json_data = response.json()

for x in json_data['rooms']:
    print(x['name'])
