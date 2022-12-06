import os
import requests
from dotenv import load_dotenv
load_dotenv()
import csv

key = (f'Bearer {os.getenv("ZOOM_TOKEN")}')
headers = {'Authorization': key}

if len(sys.argv) == 1:
    fname = sg.popup_get_file('Choose your file')
else:
    fname = sys.argv[1]

with open(fname) as f:
    reader = csv.reader(f)
    for zoomRoomEmail, in reader:

