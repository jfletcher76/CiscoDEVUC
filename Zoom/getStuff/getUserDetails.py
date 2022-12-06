import os
import requests
from dotenv import load_dotenv
import json
load_dotenv()

key = (f'Bearer {os.getenv("ZOOM_TOKEN")}')
headers = {'Authorization': key}

url = f"https://api.zoom.us/v2/users/{userName}"
response = requests.request("GET", url, headers=headers)
# print(response._content)
# json_data = response.json()
# print(json_data)

json_data = json.loads(response._content)
json_formatted_str = json.dumps(json_data, indent=2)
print(json_formatted_str)

# print(json_data['email'])

# for x in json_data['users']:
#     print(x['email'])
