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

config = 'config'

#Search Variable
search_conf = open(config, 'r').readlines()[0]
s = search_conf.split("search=")
x = s[1].strip()
#Subreddit variable
subreddit_conf = open(config, 'r').readlines()[1]
sub = subreddit_conf.split("subreddit=")
y = sub[1].strip()

#Debugging
print(x)
print(y)

# Feel free to edit this as you please.
subreddit = reddit.subreddit(y)
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

#Arguments
parser = argparse.ArgumentParser()
parser.add_argument('-s', help='Search function. This will replace "Search= " in the config file. Uses same search functions as reddit.')
parser.add_argument('-r', help='This option will set your subreddit in the config file')
args = parser.parse_args()

temp_log('log.txt')
log = open('log.txt', 'a+')
tmp = open('temp_log.txt', 'r+')

if args.s:
    search_arg = 'search='
    new_search = search_arg + args.s
    x = fileinput.input(files=config, inplace=1)
    for line in x:
        if search_arg in line:
            line = new_search
        print(line.strip())
    x.close()

if args.r:
    sub_arg = 'subreddit='
    newsubreddit = sub_arg + args.r
    sr = fileinput.input(files=config, inplace=1)
    for line in sr:
        if sub_arg in line:
            line = newsubreddit
        print(line.strip())
    sr.close()

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

