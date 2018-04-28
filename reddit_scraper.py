#!/usr/bin/env python

import praw
from slackclient import SlackClient
import os
import fileinput
import tempfile
import shutil
import subprocess
import difflib


reddit = praw.Reddit(client_id='0tV6hcxX9LPmXw', \
                    client_secret='I9qlilfmwqRc-7L-LX3jp03rX-M', \
                    user_agent='Data_Scrape', \
                    username='dalesnail', \
                    password='Sp1tf1re')

subreddit = reddit.subreddit('mechmarket')
search = input('Search: ')
search_subreddit = subreddit.search(search, sort='new', limit=25, time_filter='hour')

# Remember to export SLACK_BOT_TOKEN="My API Token"
def slack_message(message, channel):
    token = os.environ["SLACK_BOT_TOKEN"]
    sc = SlackClient(token)
    sc.api_call('chat.postMessage', channel=channel,
            text=message, username='My reddit Bot',
            icon_emoji=':robot_face:')

def temp_log(src):
    temp_dir = '/home/dalesnail/ex/scraper/'
    temp_path = os.path.join(temp_dir, 'temp_log.txt')
    shutil.copy2(src, temp_path)
    return temp_path

temp_log('log.txt')
log = open('log.txt', 'a+')
tmp = open('temp_log.txt', 'r+')

for submission in search_subreddit:
    topics_dict = f"{submission.title} : {submission.shortlink}"
    log.seek(0)
    log.write(f'{topics_dict}\n')


subprocess.check_call(['sort', '-u', '-o', 'log.txt', 'log.txt'])
diff = difflib.ndiff(log.readlines(), tmp.readlines())
for line in diff:
    minus = '-'
    channel = 'UABLM0KRP'
    if line[0] == minus:
        print(line)
        slack_message(line, channel)

    #slack_message(topics_dict, channel)
