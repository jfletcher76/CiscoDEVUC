import os
import csv
from dotenv import load_dotenv
import requests
import sys
import PySimpleGUI as sg

# Code to execute pop up box for file selection on your local machine
sg.theme("SystemDefault")
layout = [
  [sg.T("")], 
  [sg.Text("Choose a file: "), sg.Input(), sg.FileBrowse(key="-IN-")], 
  [sg.Checkbox('Change PROD???', default=False, key='IN_PROD')], 
  [sg.Button("Submit")]
  ]

###Building Window
window = sg.Window('CSV File Browser', layout, size=(600,150))
    
event, values = window.read()
if event == sg.WIN_CLOSED or event=="Exit":
    sys.exit('\nJob Terminated.  Exiting Script.\n')
elif event == "Submit":
    inProd=values['IN_PROD']
    window.close()

if inProd == 'True':
  load_dotenv()
  key = 'Bearer ' + os.getenv('ZOOM_TOKEN')
else:
  load_dotenv()
  key = 'Bearer ' + os.getenv('ZOOM_DEV_TOKEN')

payload_obj = {
    'action': 'disassociate',
    'transfer_email': 'false',
    'transfer_meeting': 'false',
    'transfer_webinar': 'false',
    'transfer_recording': 'false',
    'transfer_whiteboard': 'false'
    }
headers = {
  'Content-Type': 'application/json',
  'Authorization': key
}  

# Deletes a single user, was used for initial development and testing of script
# url = f"https://api.zoom.us/v2/users/john.doe@hotmail.com"
# response = requests.request("DELETE", url, headers=headers, data=payload_obj)
# print("API call response code is: ", response.status_code) if response.status_code == 204 else sys.exit('API Call Failed, quitting.')

with open(values["-IN-"]) as csv_file:
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
print("\nUsers to be Deleted: ", loaded)
input("press any key to deactivate")
print('')

for user in users:
    print("delete user: ", user)
    url = f"https://api.zoom.us/v2/users/{user}"
    response = requests.request("DELETE", url, headers=headers, data=payload_obj)
    if response.status_code == 204:
      print(f'User {user} disassociated.  Response code is: ', response.status_code)
    else:
      print(f'API Call Failed on user {user}, moving on to next user. Response code is: ', response.status_code)
  
print('\nJOB COMPLETE!!')
