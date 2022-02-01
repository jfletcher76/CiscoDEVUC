# This is a script I wrote to take in SMS from a hosted number at TWILIO.  The number belongs to ATT but is hosted for SMS with TWILIO
# So SMS to the number from outside will hit the webhook in twilio and send to this flask server
# Server will then send the SMS over to slack
# Slack replies will do the same in reverse
# Much of this script came from TWILIO documentation at https://www.twilio.com/blog/build-sms-slack-bridge-python-twilio
# I have added a good deal of slack API logic to build channels, add people to channels, etc.  So there's modifications to the code provided by TWILIO on their page above

# You will need to modify script with your slack team instance ID and put in a user ID.  I wrote all this for testing a theory so it is not truly done
# You might want to do more work on getting the user ID to be variablized.  If I ever pick this pack up and do that i'll update this script
# Right now this is a good framework for building something :)

import os
import slack
import re
from dotenv import load_dotenv
from flask import Flask, request, Response
from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse
load_dotenv()

app = Flask(__name__)

slack_token = os.getenv("SLACK_BOT_TOKEN")
slack_client = slack.WebClient(slack_token)
account_sid = os.getenv('TWILIO_ACCOUNT_SID')
auth_token = os.getenv('TWILIO_AUTH_TOKEN')
twilio_client = Client()

def parse_message(attributes):
    if 'event' in attributes and 'thread_ts' in attributes['event']:
        return attributes['event']['thread_ts'], attributes['event']['text'], attributes['event']['channel']
    return None, None, None

def get_to_number(incoming_slack_message_id, channel):
    data = slack_client.conversations_history(channel=channel, latest=incoming_slack_message_id, limit=1, inclusive=1)
    if 'subtype' in data['messages'][0] and data['messages'][0]['subtype'] == 'bot_message':
        text = data['messages'][0]['text']
        phone_number = extract_phone_number(text)
        return phone_number
    return None

def extract_phone_number(text): 
    data = re.findall(r'\w+', text)
    if len(data) >= 4: 
      return data[3]
    return None

@app.route('/incoming/twilio', methods=['POST'])
def send_incoming_message():
    from_number = request.form['From']
    sms_message = request.form['Body']
    message = f"Text message from {from_number}: {sms_message}"
    # Next one line remove + from e164 number for channel name else slack barfs at having + in channel name
    slackChan=from_number[1:]
    chanName=('txts-' + slackChan)

    # Get the list of channels
    result = slack_client.conversations_list()

    # Create a blank DB to add channel names to    
    channelDB=[]

    # Get channel names and add them to the DB
    for x in result['channels']:
        channelDB.append(x['name'])

    # If channel name exists, then simply send a message to it.  If not, create it, then send a message to it.     
    if chanName in channelDB:
        print('')
        print('Channel Exists')
        slack_message = slack_client.chat_postMessage(
            channel=(chanName), text=message, icon_emoji=':robot_face:')
        response = MessagingResponse()
        return Response(response.to_xml(), mimetype="text/html")
    else:
        result = slack_client.conversations_create(
        name=(chanName),
        team_id='<enter team ID>', # Enter your team ID here
        is_private='false'
        )

        # Gets the channel ID of the newly created channel to use in the invite
        newChannelID=result['channel']['id']

        # Pulls the user into the channel for the SMS message
        result = slack_client.conversations_invite(
            channel=newChannelID,
            users='<enter your user ID here>' # Enter user ID here
        )

        slack_message = slack_client.chat_postMessage(
            channel=(chanName), text=message, icon_emoji=':robot_face:')
        response = MessagingResponse()
        return Response(response.to_xml(), mimetype="text/html")

@app.route('/incoming/slack', methods=['POST'])
def send_incoming_slack():
    attributes = request.get_json()
    if 'challenge' in attributes:
        return Response(attributes['challenge'], mimetype="text/plain")
    incoming_slack_message_id, slack_message, channel = parse_message(attributes)
    if incoming_slack_message_id and slack_message:
        to_number = get_to_number(incoming_slack_message_id, channel)
        if to_number:
            messages = twilio_client.messages.create(
                to=to_number, from_=os.getenv("TWILIO_NUMBER"), body=slack_message)
        return Response()
    return Response()


if __name__ == '__main__':
    app.run()