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
config = 'config'

# This series of opens below may look odd to someone more versed in python, but I just could not get the variables working in another more concise way. Will improve later when I have a better grasp on this. 
#Search Variable
search_conf = open(config, 'r').readlines()[0]
s = search_conf.split("search=")
x = s[1].strip()
#Subreddit variable
subreddit_conf = open(config, 'r').readlines()[1]
sub = subreddit_conf.split("subreddit=")
y = sub[1].strip()
#UN
un_config = open(config, 'r').readlines()[2]
un = un_config.split("user=")
u = un[1].strip()
#PW
pw_config = open(config, 'r').readlines()[3]
pw = pw_config.split("password=")
p = pw[1].strip()
#Cid
cid_config = open(config, 'r').readlines()[4]
cid = cid_config.split("clientid=")
c = cid[1].strip()
#Secret
secret_config = open(config, 'r').readlines()[5]
secret = secret_config.split("clientsecret=")
cs = secret[1].strip()
#Debugging
print(x)
print(y)
print(u)
print(p)
print(c)
print(cs)

reddit = praw.Reddit(client_id=c, \
                    client_secret=cs, \
                    user_agent='Data_Scrape', \
                    username=u, \
                    password=p)

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

def config_change(option, arg):
    new_option = option + arg
    x = fileinput.input(files=config, inplace=1)
    for line in x:
        if option in line:
            line = new_option
        print(line.strip())
    x.close()

#Arguments
parser = argparse.ArgumentParser()
parser.add_argument('-s', help='Search function. This will replace "Search= " in the config file. Uses same search functions as reddit.')
parser.add_argument('-r', help='This option will set your subreddit in the config file')
parser.add_argument('-u', help='This option changes your username.')
parser.add_argument('-p', help='This option changes your password.')
parser.add_argument('-cid', help='This option changes the client ID provided by Reddit')
parser.add_argument('-secret', help='This option changes the "secret" provided by reddit')
args = parser.parse_args()

temp_log('log.txt')
log = open('log.txt', 'a+')
tmp = open('temp_log.txt', 'r+')

if args.s:
    config_change('search=', args.s)

if args.r:
    config_change('subreddit=', args.r)

if args.u:
    config_change('user=', args.u)

if args.p:
    config_change('password=', args.p)

if args.cid:
    config_change('clientid=', args.cid)

if args.secret:
    config_change('clientsecret=', args.secret)

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

