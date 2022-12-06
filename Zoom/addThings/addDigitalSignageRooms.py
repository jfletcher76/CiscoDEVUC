import csv
import requests
import json
import os
import csv
from dotenv import load_dotenv

load_dotenv()
key = 'Bearer ' + os.getenv('ZOOM_TOKEN')



new_room_url = "https://api.zoom.us/v2/rooms"


with open('c:/temp/adesa_rooms.csv') as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    line_count = 0
    for row in csv_reader:
        if line_count == 0:
            print(f'Column names are {", ".join(row)}')
            line_count += 1
        else:
            print("creating room: ", row[0], "location ID: ", row[1])
            
            payload_obj={
            'name': row[0],
            'type': 'DigitalSignageOnly',
            'location_id': row[1]
            }
            
            headers = {
            'Content-Type': 'application/json',
            'Authorization': key
            }

            payload = json.dumps(payload_obj)
            input("press a key to continue: ")

            response = requests.request("POST", new_room_url, headers=headers, data=payload)

            print(response.text)