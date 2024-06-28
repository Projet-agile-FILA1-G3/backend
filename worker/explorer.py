import logging

import requests
from bs4 import BeautifulSoup

from shared.db import get_session
from shared.models.Feed import Feed
from shared.models.Item import Item
from shared.persistence.FeedRepository import FeedRepository
from worker.parsing.feed_parsing import crawl_feed

session = get_session()
feedRepository = FeedRepository(session)


# These functions are used to explore a website to find a new rss feed on it.

def explore(item: Item):
    if item.audio_link != None:
        return True

    logging.info(f'Exploring {item.link}')
    response = requests.get(item.link, headers={"User-Agent": "curl/7.64.1"}).text
    new_links = extract_links(response)
    logging.info(f'Found {len(new_links)} new links')
    for new_link in new_links:
        if not new_link.startswith('http'):
            new_link = transform_url(item.link) + new_link

        # Condition to skip exploring
        if feedRepository.exists_url(new_link):
            continue

        feed = Feed(url=new_link, title="", description="", last_fetching_date=None)
        try:
            feed = crawl_feed(feed, with_items=False)
        except Exception as e:
            logging.error(f'Failed to crawl feed {new_link}: {e}')
            logging.debug(f'Failed to crawl feed {new_link}: {e}', exc_info=True)
            continue

        # Default language is the language of the parent feed
        if feed.lang is None:
            feed.lang = item.feed.lang

        feedRepository.store(feed)
        logging.info(f'Found new feed {new_link}')


def transform_url(url: str):
    return url.split('//')[1].split('/')[0]


def extract_links(response):
    soup = BeautifulSoup(response, 'html.parser')
    link_tags = soup.find_all('link')
    links = [link.get('href') for link in link_tags if (link.get('href') and link.get('type') == "application/rss+xml")]
    valid_links = get_not_saved_links(links)

    return valid_links


def get_not_saved_links(links):
    saved_feeds = feedRepository.find_all()
    links_in_db = [feed.url for feed in saved_feeds]
    valid_links = list(set(links) - set(links_in_db))
    return valid_links
