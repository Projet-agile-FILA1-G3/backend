import logging
from queue import Queue

import schedule

from shared.db import get_session
from shared.persistence.FeedRepository import FeedRepository

UPDATING_INTERVAL = 1800
FEED_FETCHING_INTERVAL = 1800

logger = logging.getLogger(__name__)

session = get_session()
feedRepository = FeedRepository(session)


def scheduler_init(queue: Queue):
    add_all_to_queue(queue)
    schedule.every(UPDATING_INTERVAL).seconds.do(add_all_to_queue, queue)


def add_all_to_queue(queue: Queue):
    feeds = feedRepository.find_all()
    for feed in feeds:
        logging.info(f'Adding feed {feed.url} to fetch queue')
        queue.put(feed.id)
