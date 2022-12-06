import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()
key = 'Bearer ' + os.getenv('ZOOM_TOKEN')


payload_obj = {}
headers = {
  'Content-Type': 'application/json',
  'Authorization': key
}

payload = json.dumps(payload_obj)




city_url = f"https://api.zoom.us/v2/rooms/locations?parent_location_id={ID}&type=city&page_size=100"
campus_url = f"https://api.zoom.us/v2/rooms/locations?parent_location_id={ID}&type=campus&page_size=100"


city_response = requests.request("GET", city_url, headers=headers, data=payload)
campus_response = requests.request("GET", campus_url, headers=headers, data=payload)


locations = json.loads(city_response.text)
campuses = json.loads(campus_response.text)

campus = (campuses['locations'])
cities = (locations['locations'])


for city in cities:

  for camp in campus:
    if camp['parent_location_id'] == city['id']:
      print(city['id'], city['name'], camp['id'], camp['name'])





    
