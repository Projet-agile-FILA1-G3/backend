import logging
from queue import Queue

import schedule
from sqlalchemy import UUID
import shared.models.Feed as Feed
from shared.db import get_session

UPDATING_INTERVAL = 1800
FEED_FETCHING_INTERVAL = 2700

scheduled_feeds = set()
logger = logging.getLogger(__name__)


def scheduler(queue: Queue):
    logger.info('Scheduler started')
    scheduler_init(queue)
    schedule.every(FEED_FETCHING_INTERVAL).seconds.do(lambda: scheduler_init(queue))
    while True:
        schedule.run_pending()


def scheduler_init(queue: Queue):
    session = get_session()
    feeds = Feed.find_all(session)
    session.close()

    for feed in feeds:
        schedule_feed(feed.id, queue)
        # and run once immediately
        add_feed(feed.id, queue)


def schedule_feed(feed_id: UUID, queue: Queue):
    if is_feed_scheduled(feed_id):
        logger.info(f'Feed {feed_id} already scheduled')
        return
    schedule.every(UPDATING_INTERVAL).seconds.do(lambda: add_feed(feed_id, queue), tag=f'feed_{feed_id}')
    scheduled_feeds.add(feed_id)
    logger.info(f'Scheduled feed {feed_id}')


def add_feed(feed_id: UUID, queue: Queue):
    queue.put(feed_id)


def is_feed_scheduled(feed_id: UUID) -> bool:
    return feed_id in scheduled_feeds
