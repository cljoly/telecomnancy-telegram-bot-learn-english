#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Extract article from various sources

import feedparser as fd

# Sources of news
# TODO Add more
sources = {'The Economist - World News': 'https://www.economist.com/rss'}


def getTitleUrl(feed):
    """ Get all title and url of article in a feed """
    return map(lambda f: (f.title, f.link), feed.entries)


def getFeed(sourceName):
    """ Get the feed associated with a name from sources """
    feed_url = sources[sourceName]
    feed = fd.parse(feed_url)
    return feed
