#! /usr/bin/env python3

import sys
from slacker import Slacker, Error

# Get channel name from command line
try:
    channel_name = sys.argv[1].strip('\'"')
    assert channel_name
except:
    print("Please specify a channel name")
    sys.exit(1)

# Load API key from apikey.txt
try:
    with open('apikey.txt') as f:
        api_key = f.read().strip()
        assert api_key
except IOError:
    print("Cannot find apikey.txt, or other reading error")
    sys.exit(1)
except AssertionError:
    print("Empty API key")
    sys.exit(1)
else:
    slack = Slacker(api_key)

# Get channel id from name
response = slack.channels.list()
channels = [d for d in response.body['channels'] if d['name'] == channel_name]
if not len(channels):
    print("Cannot find channel")
    sys.exit(1)
assert len(channels) == 1
channel_id = channels[0]['id']

# Get users list
response = slack.users.list()
users = [(u['id'], u['name'], u['profile']['real_name']) for u in response.body['members'] if u['is_bot'] == False and u['deleted'] == False]

# Invite all users to slack channel
print("***** INVITATION OF {} MEMBERS IN PROGRESS TO CHANNEL : {} *****".format(len(users), channel_name))

for user_id, user_name, user_full_name in users:
    print("Inviting [ID: %s] %s (aka %s)" % (user_id, user_full_name, user_name))
    try:
        slack.channels.invite(channel_id, user_id)
        print("\t --> OK")
    except Error as e:
        code = e.args[0]
        if code == "already_in_channel":
            print("{} is already in the channel".format(user_name))
        elif code in ('cant_invite_self', 'cant_invite', 'user_is_ultra_restricted'):
            print("Skipping user {} ('{}')".format(user_name, code))
        else:
            raise
