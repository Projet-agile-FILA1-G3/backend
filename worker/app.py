import logging

from worker.crawler import crawl_feed_id

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    logging.info("Starting worker")
    print("Starting worker")

    crawl_feed_id('c89b1338-395a-4de6-9ef7-b8e5490385b8')







