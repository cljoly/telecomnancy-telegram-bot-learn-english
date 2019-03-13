#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Extract article from various sources

import feedparser as fd
from random import randint

# Sources of news (mainly world news, could be insterresting for anyone)
sources = {'The Economist - World News': 'https://www.economist.com/rss',
           'The Guardian - International':
           'https://www.theguardian.com/international/rss',
           'The Independant - World':
           'http://www.independent.co.uk/news/world/rss',
           'Washington Post - Word':
           'http://feeds.washingtonpost.com/rss/world',
           'Washington Post - Lifestyle':
           'http://feeds.washingtonpost.com/rss/lifestyle',
           'Reuters - Business News':
           'http://feeds.reuters.com/reuters/businessNews',
           'Reuters - Word News':
           'http://feeds.reuters.com/Reuters/worldNews',
           'The Telegraph': 'https://www.telegraph.co.uk/rss.xml'
           }


def getTitleUrl(feed):
    """ Get all title and url of article in a feed """
    return map(lambda f: (f.title, f.link), feed.entries)


def getFeed(sourceName):
    """ Get the feed associated with a name from sources """
    feed_url = sources[sourceName]
    feed = fd.parse(feed_url)
    return feed

def random_from_subscribed(db, user):
    subs = db.get_subscriptions(user)
    while True:
        feed = getFeed(subs[randint(0, len(subs)-1)])
        for r in getTitleUrl(feed):
            print("Got random: ", r)
            return r

def toggle_subscription(db, user, sourceName):
    """ Subcribe or unscribe user to given news source. Return True if
        subscribed, False if unscribed """
    if not db.has_subscription(user, sourceName):
        print("sub")
        db.add_subscription(user, sourceName)
        return True
    else:
        print("unsub")
        db.delete_subscription(user, sourceName)
        return False
