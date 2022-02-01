# This script will get a channel ID from a slack instance.  You will need a bot and team ID for it to work

from hashlib import new
from dotenv import load_dotenv
load_dotenv()
import logging
import os
# Import WebClient from Python SDK (github.com/slackapi/python-slack-sdk)
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

# WebClient instantiates a client that can call API methods
# When using Bolt, you can use either `app.client` or the `client` passed to listeners.
#client = WebClient(token=os.environ.get("SLACK_BOT_TOKEN"))
client = WebClient(token=os.getenv("SLACK_BOT_TOKEN"))
logger = logging.getLogger(__name__)

result = client.conversations_create(
    name="<enter your channel name here>", # Channel name here
    team_id='<enter your team ID>', # Team ID here
    is_private='true'
)
newChannelID=result['channel']['id']

print(result)
print('')
print(newChannelID)