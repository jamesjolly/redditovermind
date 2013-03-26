#!/usr/bin/env python
"""
redditovermind 0.1
Copyright (C) 2013, James Jolly
See MIT-LICENSE.txt for legalese and README.md for usage.
"""

c_DATA_DIR = 'data' # empty dir to put the reddit post outfiles

c_TARGET_SUBREDDIT = 'worldnews' # what do you wish to mine today?

c_BATCH_WRITE = 10
c_MAX_PER_GRAB = 1000
c_SLEEP_BETWEEN_TRIES = 1800

c_USER_AGENT = 'descriptive reddit miner user agent'
c_USER = 'reddit username'
c_PASS = 'reddit password'

c_MAX_REPLACES = 100 # don't surface too much deeply hidden content per url
c_HAS_REPLIES = 5 # only dive into hidden content when there enough replies to it

import praw
import pickle
import requests
from time import sleep

def write_posts(posts, grab_id, dump_id):
    # send these to a database IRL =)
    outfile = c_DATA_DIR + '/out_' + str(grab_id) + '_' + str(dump_id) + '.pkl'
    pickle.dump(posts, open(outfile, 'wb'))
    print 'saved', outfile

def grab(subreddit, seen, grab_id):
    dump_id = 0
    posts = [ ]
    for post in subreddit.get_hot(limit=c_MAX_PER_GRAB):
            
            print 'grabbed post', post.name
            if post.name in seen:
                continue
            
            post.replace_more_comments(limit=c_MAX_REPLACES, threshold=c_HAS_REPLIES)            
            post_data = {
                'name': post.name,
                'url': post.url,
                'ups': post.ups,
                'downs': post.downs,
                'comments': [c.body for c in praw.helpers.flatten_tree(post.comments)
                             if getattr(c, 'body', False)]
            }
            
            seen.add(post.name)
            posts.append(post_data)
            
            if len(posts) >= c_BATCH_WRITE:
                write_posts(posts, grab_id, dump_id)
                posts = [ ]
                dump_id += 1
            
    if len(posts) > 0:
        write_posts(posts, grab_id, dump_id)

if __name__ == "__main__":
    
    grab_id, seen = 0, set()
    
    while True:
        
        try:
            reddit_conn = praw.Reddit(user_agent=c_USER_AGENT)
            reddit_conn.login(c_USER, c_PASS)
            subreddit = reddit_conn.get_subreddit(c_TARGET_SUBREDDIT)
            grab(subreddit, seen, grab_id)
        except requests.exceptions.ConnectionError:
            pass
        
        grab_id += 1
        sleep(c_SLEEP_BETWEEN_TRIES)
        
