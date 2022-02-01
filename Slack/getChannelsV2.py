# Was using this for testing some stuff for the twilio2slacksms script.  Might need some tweaking to get working if you need it

import os
import logging
#import slack
from dotenv import load_dotenv
load_dotenv()
from slack_sdk import WebClient


slack_client = WebClient(token=os.getenv("SLACK_BOT_TOKEN"))

print('')
from_number=input('Enter phone number: ')
#from_number=(f'+{from_number}')
chanName=(f'msgs-{from_number}')
print('')

result = slack_client.conversations_list()
#print(result)
        
channelDB=[]
for x in result['channels']:
    channelDB.append(x['name'])
    #print(x['name'])

print(channelDB)

if chanName in channelDB:
    print('')
    print('Channel Exists')
else:
    print('')
    print('Channel doesn\'t exist')
    # print('')
    # print(f'Creating channel {channelName}')
    #     slackChan = from_number[1:]
    # result = slack_client.conversations_create(
    # name=('sms-' + slackChan),
    # team_id='<enter team ID>', # Team ID here
    # is_private='true'
    # )
    # # Gets the channel ID of the newly created channel to use in the invite
    # newChannelID=result['channel']['id']

    # # Pulls the user into the channel for the SMS message
    # result = slack_client.conversations_invite(
    #     channel=newChannelID,
    #     users='<enter user id here>' # User ID here
    # )

    # # Log the result which includes information like the ID of the conversation
    # logger.info(result)
    # print('try done')

    # except SlackApiError as e:
    #     logger.error("Error creating conversation: {}".format(e))



