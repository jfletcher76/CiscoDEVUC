import os
import requests
from dotenv import load_dotenv
load_dotenv()

import sys
import PySimpleGUI as sg
import csv

key = (f'Bearer {os.getenv("ZOOM_TOKEN")}')
headers = {'Authorization': key}

# Code to execute pop up box for file selection on your local machine
if len(sys.argv) == 1:
    fname = sg.popup_get_file('Choose your file')
else:
    fname = sys.argv[1]

with open(fname) as f:
    reader = csv.reader(f)
    for zoomRoomName, newRoomEmail in reader:    
        # Gets the zoom room ID based off the name
        print('\nNext Calendar Starting update')
        print('-' * 20)
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
        # print('\n', json_data)
        print(f'Calendar Resource ID: ' + json_data['basic'].get('calendar_resource_id'))
        try:
            url = f"https://api.zoom.us/v2/rooms/calendar/services/{ZOOM_ID}/resources/{json_data['basic']['calendar_resource_id']}"
            response = requests.request("GET", url, headers=headers)
            json_data2 = response.json()
            print('Current zoom room calendar resource email: ' + json_data2['calendar_resource_email'])
            print(f'Room will change to this email: {newRoomEmail}')

        except:
            print('Current zoom room calendar resource email: None')

        # Builds the calendar resource in the serivce account
        req = {
            'calendar_resource_email': newRoomEmail,
            'calendar_resource_name': newRoomEmail
        }

        try:
            resp = requests.post( 
                f"https://api.zoom.us/v2/rooms/calendar/services/{ZOOM_ID}/resources",
                    headers=headers,
                    json = req
                )
            print(f'\nCalendar resource {newRoomEmail} added successfully.!', resp)
            newCalRes = resp.json()
        except:
            print(f'\nCalendar resource {newRoomEmail} failed to add', resp)

        # print(newCalRes)

        # This will update the existing zoom room with the new calendar resource 
        req = {
            'basic': {
                'calendar_resource_id': newCalRes['calendar_resource_id']
            }
        }

        try:
            # Clear calendar resource
            resp = requests.patch( 
                f"https://api.zoom.us/v2/rooms/{zoomRoomId}",
                headers=headers,
                json = {
                    'basic': {
                        "calendar_resource_id": ""
                    }
                }
            )
            print(f'\nSuccessfully removed old calendar resource.', resp)
            # Assign new calendar resource
            resp = requests.patch( 
                f"https://api.zoom.us/v2/rooms/{zoomRoomId}",
                headers=headers,
                json = req
            )
            # print(resp.content)
            print(f'Successfully updated {zoomRoomName}', resp)
            print('-' * 20)
            print('Calendar update ending, next up!!!\n')
        except:
            print(f'\nFailed to update {zoomRoomName}', resp)

        print('\nJob Complete')
