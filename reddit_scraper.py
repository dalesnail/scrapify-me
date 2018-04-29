#!/usr/bin/env python

import argparse
import praw
from slackclient import SlackClient
import os
from os.path import expanduser
import fileinput
import tempfile
import shutil
import subprocess
import difflib

home = expanduser('~')
reddit = praw.Reddit(client_id='0tV6hcxX9LPmXw', \
                    client_secret='I9qlilfmwqRc-7L-LX3jp03rX-M', \
                    user_agent='Data_Scrape', \
                    username='dalesnail', \
                    password='Sp1tf1re')

subreddit = reddit.subreddit('mechmarket')
config = 'config'
conf = open(config, 'r')
search = conf.readlines()[0] #input('Search: ')
subreddit = conf.readlines()[1]
#s = search.readlines()[0]
s = search.split("search=")
sub = subreddit.split("subreddit=")
x = s[1]
y = sub[1]
print(x)
print(y)
# Feel free to edit this as you please.
search_subreddit = subreddit.search(x, sort='new', limit=25, time_filter='hour')

# Remember to export SLACK_BOT_TOKEN="My API Token"
def slack_message(message, channel):
    token = os.environ["SLACK_BOT_TOKEN"]
    sc = SlackClient(token)
    sc.api_call('chat.postMessage', channel=channel,
            text=message, username='My reddit Bot',
            icon_emoji=':robot_face:')

def temp_log(src):
    temp_dir = f'{home}/scrapify-me/'
    temp_path = os.path.join(temp_dir, 'temp_log.txt')
    shutil.copy2(src, temp_path)
    return temp_path

parser = argparse.ArgumentParser()
parser.add_argument('-s', help='Search function. This will replace "Search= " in the config file. Uses same search functions as reddit.')
args = parser.parse_args()

temp_log('log.txt')
log = open('log.txt', 'a+')
tmp = open('temp_log.txt', 'r+')

if args.s:
    search = 'search='
    new_search = search + args.s
    x = fileinput.input(files=config, inplace=1)
    for line in x:
        if search in line:
            line = new_search
        print(line.strip())
    x.close()

if not any(vars(args).values()):
    for submission in search_subreddit:
        topics_dict = f"{submission.title}: {submission.shortlink}"
        log.seek(0)
        log.write(f'{topics_dict}\n')
        #print(topics_dict)
    subprocess.check_call(['sort', '-u', '-o', 'log.txt', 'log.txt'])
    diff = difflib.ndiff(log.readlines(), tmp.readlines())
    for line in diff:
        minus = '-'
        channel = 'UABLM0KRP'
        if line[0] == minus:
            print(line)
            slack_message(line, channel)

