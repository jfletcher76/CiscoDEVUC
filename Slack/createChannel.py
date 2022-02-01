# This script was used in testing how to create channels in a slack.  You will need a bot, a team ID, and a user ID for this script to work
# Or you can tailor it to how you need it to work

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

from_number='+15551231235'

try:
    slackChan = from_number[1:]
    result = client.conversations_create(
    name=('sms-' + slackChan),
    team_id='<enter your team ID>', # I was using my own for testing purposes.
    is_private='true'
    )
    # Gets the channel ID of the newly created channel to use in the invite
    newChannelID=result['channel']['id']

    # Pulls the user into the channel for the SMS message
    result = client.conversations_invite(
        channel=newChannelID,
        users='<enter your user ID>' # I was using my own for testing purposes
    )

    # Log the result which includes information like the ID of the conversation
    logger.info(result)
    print('try done')

except SlackApiError as e:
    logger.error("Error creating conversation: {}".format(e))