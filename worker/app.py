import logging
import os

from queue import Queue
from threading import Thread
from time import sleep

import schedule

from shared.db import init_db
from worker.scheduler import scheduler_init

if os.getenv('ENV') != 'production':
    from dotenv import load_dotenv
    load_dotenv()

from worker.crawler import crawler

if __name__ == '__main__':
    # Initialize logging
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')
    log_level = logging.getLevelName(os.getenv('LOG_LEVEL', 'INFO'))
    logging.getLogger().setLevel(log_level)
    logging.info("Starting worker")

    try:
        init_db()
    except:
        logging.error(f"Failed to initialize database: {os.getenv('POSTGRES_HOST')}")
        exit(1)

    # Init APP
    feed_to_crawl = Queue()
    scheduler_init(feed_to_crawl)

    crawler(feed_to_crawl)
    Thread(target=crawler, args=(feed_to_crawl,)).start()

    while True:
        schedule.run_pending()
        sleep(1)
