# This script adds an email to the calendar service account so you can add the calendar to the zoom room in another step if you want

import os
import requests
from dotenv import load_dotenv
load_dotenv()

key = (f'Bearer {os.getenv("ZOOM_TOKEN")}') # Remove or ADD DEV if you want to use this in prod or dev respectively
headers = {'Authorization': key}

# This will get the Calendar Service ID to add the email to the service account
url = f"https://api.zoom.us/v2/rooms/calendar/services"
response = requests.request("GET", url, headers=headers)
json_data = response.json()
print('\n', json_data)

# Assigns Variable for the post
calendarServicveID=json_data['calendar_services'][0]['calendar_service_id']
print(calendarServicveID)

# Builds the calendar resource in the serivce account
req = {
    'calendar_resource_email': 'email@email.net',
    'calendar_resource_name': 'email@email.net'
}

try:
    resp = requests.post( 
        f"https://api.zoom.us/v2/rooms/calendar/services/{calendarServicveID}/resources",
        headers=headers,
        json = req
        )
    print('\nCalendar resource added successfully.!', resp)
except:
    print(f'\nCalendar resource failed to add', resp)

print('Job Complete!\n')