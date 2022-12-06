# This script will run through a csv file and deactivate all the accounts you give it
# file format for CSV is column header needs to be "user" for A1 cell
# Everything from A2 and on is first.last@domain.com 

import os
import csv
from dotenv import load_dotenv
import requests
import sys
import PySimpleGUI as sg

# Code to execute pop up box for file selection on your local machine
sg.theme('SystemDefault')
layout = [
  [sg.T('')], 
  [sg.Text('Choose a file: '), sg.Input(), sg.FileBrowse(key='-IN-')], 
  [sg.Checkbox('Change PROD???', default=False, key='-IN_PROD-')], 
  [sg.Button('Submit')]
  ]

###Building Window
window = sg.Window('CSV File Browser', layout, size=(600,150))
    
event, values = window.read()
if event == sg.WIN_CLOSED or event=="Exit":
    sys.exit('\nJob Terminated.  Exiting Script.\n')
elif event == "Submit":
    # inProd=values['-IN_PROD-']
    window.close()

# This allows you to use same script to run against PROD and DEV
if values['-IN_PROD-'] == True:
  load_dotenv()
  key = 'Bearer ' + os.getenv('ZOOM_TOKEN')
else:
  load_dotenv()
  key = 'Bearer ' + os.getenv('ZOOM_DEV_TOKEN')

# params to pass in url
params = {'action': "deactivate"}
headers = {
  'Content-Type': 'application/json',
  'Authorization': key
}  

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
print("\nUsers to be deactivated: ", loaded)
input("press any key to deactivate")
print('')

for user in users:
    print("Deactivate user: ", user)
    # Run the deactivate!!
    response = requests.put( 
        f"https://api.zoom.us/v2/users/{user}/status",
        headers=headers,
        json = params
      )

    if response.status_code == 204:
      print(f'User {user} deactivated.')
    else:
      print(f'API Call Failed on user {user}, moving on to next user. Response code is: ', response.text)
  
print('\nJOB COMPLETE!!')
