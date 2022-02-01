# This script will pull a list of public channels from your slack instance.  It CAN NOT get private channels
# You will need only a bot for this 

import os
from dotenv import load_dotenv
load_dotenv()
from slack_sdk import WebClient

slack_client = WebClient(token=os.getenv("SLACK_BOT_TOKEN"))

result = slack_client.conversations_list()

print('Channel List')
print('-' * 40)
channelDB=[]
for x in result['channels']:
    print(x['name'])

print('')
print('List Complete')