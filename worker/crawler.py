import logging
from queue import Queue
from time import sleep

import schedule

from shared.db import get_session
from shared.exception import EntityNotFoundException
from shared.persistence.FeedRepository import FeedRepository
from shared.persistence.ItemRepository import ItemRepository
from worker.crawling_notifyer import notify_api
from worker.explorer import explore
from worker.indexer import index_item
from worker.parsing.feed_parsing import crawl_feed

session = get_session()
feedRepository = FeedRepository(session)
itemRepository = ItemRepository(session)


def crawler(queue: Queue):
    logging.info('Starting crawler')
    # Wait for new item to crawl
    while True:
        schedule.run_pending()
        feed_id = queue.get()
        if feed_id is None:
            # reduce cpu intensiveness of the app
            sleep(60)
            break
        try:
            crawl_items_of_feed_id(feed_id)
        except Exception as e:
            logging.error(f'Failed to crawl feed {feed_id}: {e}')
            logging.debug(f'Failed to crawl feed {feed_id}: {e}', exc_info=True)
        queue.task_done()
        logging.info(f'Finished crawling feed {feed_id}')


def crawl_items_of_feed_id(feed_id):
    feed_db = feedRepository.find_by_id(feed_id)

    if feed_db is None:
        raise EntityNotFoundException(f'Feed {feed_id} not found')
    logging.info(f'Crawling feed {feed_db.url}')

    crawled_feed = crawl_feed(feed_db)
    crawled_feed.id = feed_id

    items = crawled_feed.items

    for item in items:
        item.feed = feed_db
        if not itemRepository.exists(item):
            itemRepository.store(item)

            # Indexing
            index_item(item)

            # Exploring
            explore(item)

    feedRepository.update_last_fetching_date(feed_id)
    notify_api(feed_db.url)
    logging.info(f'Finished crawling feed {feed_db.url}')
