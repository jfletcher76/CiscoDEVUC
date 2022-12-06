import os
import requests
from dotenv import load_dotenv
load_dotenv()

import sys
import PySimpleGUI as sg
import csv

# This will output to a file manually because I was being lazy
filePath = 'c:\pythonoutput\getZoomRoomList_output_FINALCHECK.txt'
outF = open(filePath, 'a') # 'a' for append 'w' for write

key = (f'Bearer {os.getenv("ZOOM_TOKEN")}')
headers = {'Authorization': key}

# Code to execute pop up box for file selection on your local machine
if len(sys.argv) == 1:
    fname = sg.popup_get_file('Choose your file')
else:
    fname = sys.argv[1]

with open(fname) as f:
    reader = csv.reader(f)
    for zoomRoomName, zoomRoomEmail in reader:  
    
        try:
            res = requests.post(
                'https://api.zoom.us/v2/rooms/zrlist',
                headers=headers,
                json={"method": "list", "params": {"zr_name": zoomRoomName}}
            )

            res.raise_for_status()
            # print(res.json())
            zoomRoomId=res.json()['result']['data'][0]['zr_id']
            print(f'Zoom room name: {zoomRoomName}  -  ZoomRoomID: {zoomRoomId}')
            print(f'Zoom room name: {zoomRoomName}  -  ZoomRoomID: {zoomRoomId}', file=outF)
            # print(f'ZoomRoomID: {zoomRoomId}')
        except:
            print(f'{zoomRoomName} didn\'t work!')
            print(f'{zoomRoomName} didn\'t work!', file=outF)

outF.close()
print('Job Complete')