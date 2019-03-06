#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Extract article from various sources

import feedparser as fd

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
