import logging
from queue import Queue

import requests

from shared.db import get_session
from shared.models import Feed
import shared.models.Item as Item
from worker.parsing.feed_parsing import RssFeedParser, AtomFeedParser


def crawler(queue: Queue):
    logging.info('Starting crawler')
    # Wait for new item to crawl
    while True:
        feed_id = queue.get()
        if feed_id is None:
            break
        logging.info(f'Started crawling feed {feed_id}')
        try:
            crawl_items_of_feed_id(feed_id)
        except Exception as e:
            logging.error(f'Failed to crawl feed {feed_id}: {e}')
        queue.task_done()
        logging.info(f'Finished crawling feed {feed_id}')


def crawl_items_of_feed_id(feed_id):
    session = get_session()
    feed = Feed.find_by_id(session, feed_id)
    session.close()

    if feed is None:
        raise Exception(f'Feed with id {feed_id} not found')

    feed = crawl_feed(feed)

    items = feed.items
    session = get_session()

    for item in items:
        item.feed_id = feed.id
        item.feed = feed
        if not Item.exists(session, item):
            Item.insert(session, item)
    session.commit()
    session.close()


def crawl_feed(feed: Feed, with_items: bool = True) -> Feed:
    raw_feed = fetch_full_raw_feed(feed)
    try:
        feed = RssFeedParser(raw_feed, url=feed.url, feed_id=feed.id).parse(with_items=with_items)
    except Exception as e:
        try:
            feed = AtomFeedParser(raw_feed, url=feed.url, feed_id=feed.id).parse(with_items=with_items)
        except Exception as e:
            logging.error(f'Failed to parse feed as RSS and Atom: {e}')
            return []
    return feed


def fetch_full_raw_feed(feed: Feed) -> str:
    response = requests.get(feed.url, headers={"User-Agent": "curl/7.64.1"})
    if response.status_code != 200:
        raise Exception(f'Failed to fetch feed {feed.url}, status code {response.status_code}')
    return response.text
