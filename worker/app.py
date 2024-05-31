import logging

from shared.db import get_session
from shared.models import Feed
from worker.crawler import crawl_feed_id

if __name__ == '__main__':
    logging.getLogger().setLevel(logging.DEBUG)
    logging.info("Starting worker")
    print("Starting worker")

    session = get_session()
    feeds = Feed.get_all(session)
    session.close()

    for feed in feeds:
        crawl_feed_id(feed.id)









