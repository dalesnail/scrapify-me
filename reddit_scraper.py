#!/usr/bin/env python

import argparse
import configargparse
import difflib
import os
from os.path import expanduser
import praw
import shutil
from slackclient import SlackClient
import subprocess
import sys


def red(client_id, client_secret, username, password, user_agent='DudeSnail_v0.1'):
    reddit = praw.Reddit(client_id=args.client_id,
                            client_secret=args.client_secret,
                            user_agent='DudeSnail_v0.1',
                            username=args.username,
                            password=args.password)
    return reddit


# Remember to export SLACK_BOT_TOKEN="My API Token"
def slack_message(message, channel, token):
    sc = SlackClient(token)
    return sc.api_call('chat.postMessage',
                       channel=channel,
                       text=message,
                       username='My reddit Bot',
                       icon_emoji=':robot_face:')


def temp_log(src):
    temp_dir = '{}/scrapify-me/'.format(home)
    temp_path = os.path.join(temp_dir, 'temp_log.txt')
    shutil.copy2(src, temp_path)
    return temp_path


home = expanduser('~')

config_path = '{}/scrapify-me/scrapify.cfg'.format(home)

if not os.path.exists(config_path):
    with open(config_path, 'w+') as f:
        f.write('''[scrapify-me]
search = 
subreddit = 
user = 
password = 
client-id = 
client-secret = 
token = 
''')
        print("Set up your config file")
        sys.exit()

if not os.path.exists('{}/scrapify-me/log.txt'.format(home)):
    open('{}/scrapify-me/log.txt'.format(home), 'a+')

# Command line args override config file options
config = configargparse.ArgumentParser(default_config_files=[config_path])
config.add('-c', '--config', required=False, is_config_file=True,
           help='Path to config file.')
config.add('-s', '--search', dest='search_term', help='Term to search for')
config.add('-r', '--subreddit', dest='sub_reddit', help='Subreddit to search within')
config.add('-u', '--username', dest='username', help='Reddit username')
config.add('-p', '--password', dest='password', help='Reddit password')
config.add('-cid', '--client-id', dest='client_id', help='Reddit Client ID')
config.add('-sec', '--client-secret', dest='client_secret', help='Reddit Client Secret')
config.add('-t', '--token', dest='token', env_var='SLACK_BOT_TOKEN', help='Slack bot token.')
config.add('-test', help='test')
args = config.parse_args()

temp_log('{}/scrapify-me/log.txt'.format(home))
log = open('{}/scrapify-me/log.txt'.format(home), 'a+')
tmp = open('{}/scrapify-me/temp_log.txt'.format(home), 'a+')

## Check which arg values have been set
print(vars(args).values())

# Feel free to edit this as you please.
subreddit = red(args.client_id,
                args.client_secret,
                args.username,
                args.password,
                user_agent='DudeSnail_v0.1').subreddit(args.sub_reddit)
search_subreddit = subreddit.search(args.search_term, sort='new', limit=25, time_filter='hour')


# May need to revist these conditionals 
for submission in search_subreddit:
    topics_dict = '{}: {}'.format(submission.title, submission.shortlink)
    log.seek(0)
    log.write('{}\n'.format(topics_dict))
        ## type(topics_dict) # this is just a string, not a dict
subprocess.check_call(['sort', '-u', '-o', '{}/scrapify-me/log.txt'.format(home), '{}/scrapify-me/log.txt'.format(home)])
diff = difflib.ndiff(log.readlines(), tmp.readlines())
for line in diff:
    channel = 'UABLM0KRP'
    if line[0] == '-':
        print(line)
        slack_message(line, channel, args.token)
