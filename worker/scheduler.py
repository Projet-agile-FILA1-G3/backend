import logging
from queue import Queue

import schedule
from sqlalchemy import UUID
from shared.db import get_session
from shared.persistence.FeedRepository import FeedRepository

UPDATING_INTERVAL = 1800
FEED_FETCHING_INTERVAL = 1800

scheduled_feeds = set()
logger = logging.getLogger(__name__)

session = get_session()
feedRepository = FeedRepository(session)


def scheduler(queue: Queue):
    logger.info('Scheduler started')
    scheduler_init(queue)
    schedule.every(FEED_FETCHING_INTERVAL).seconds.do(lambda: scheduler_init(queue)).tag('feed_scheduler')
    while True:
        schedule.run_pending()


def scheduler_init(queue: Queue):
    feeds = feedRepository.find_all()

    for feed in feeds:
        # schedule_feed(feed.id, queue)
        # and run once immediately
        add_feed(feed.id, queue)


def schedule_feed(feed_id: UUID, queue: Queue):
    if is_feed_scheduled(feed_id):
        return
    schedule.every(UPDATING_INTERVAL).seconds.do(lambda: add_feed(feed_id, queue)).tag(f'feed_{feed_id}'
                                                                                       )
    scheduled_feeds.add(feed_id)
    logger.info(f'Scheduled feed {feed_id}')


def add_feed(feed_id: UUID, queue: Queue):
    logger.info(f'Adding feed {feed_id} to queue')
    queue.put(feed_id)


def is_feed_scheduled(feed_id: UUID) -> bool:
    return feed_id in scheduled_feeds
