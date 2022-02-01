# This will simply test if you have all the stuff setup for interacting with your bot/slack

import os
import logging
from slack_sdk import WebClient

from dotenv import load_dotenv
load_dotenv()

logging.basicConfig(level=logging.DEBUG)
client = WebClient(token=os.getenv("SLACK_BOT_TOKEN"))

resp = client.api_test()