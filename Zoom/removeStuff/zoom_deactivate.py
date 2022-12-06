import requests
import json
import sys
import os
import csv
from dotenv import load_dotenv

load_dotenv()
key = 'Bearer ' + os.getenv('ZOOM_TOKEN')


payload_obj = {
    'action': 'deactivate'
    }
headers = {
  'Content-Type': 'application/json',
  'Authorization': key
}

payload = json.dumps(payload_obj)

# with open('c:/temp/disable.csv') as csv_file:
with open('c:/pythoninput/deleteZoomUsers.csv') as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    line_count = 0
    users = []
    for row in csv_reader:
        if line_count == 0:
            print(f'Column names are {", ".join(row)}')
            line_count += 1
        else:
            users.append(row[0])


loaded = len(users)
print("Users to be Deactivated: ", loaded)
input("press any key to deactivate")

for user in users:
    print("deactivating user: ", user)
    url = f"https://api.zoom.us/v2/users/{user}/status"
    response = requests.request("PUT", url, headers=headers, data=payload)
    print("API call response code is: ", response.status_code) if response.status_code == 204 else sys.exit('API Call Failed, quitting.')
