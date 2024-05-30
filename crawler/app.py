import logging
from os import getenv
from time import sleep

from dotenv import load_dotenv
import schedule
from crawler_class import Crawler

if getenv('NODE_MODE') != 'production':
    load_dotenv('.env')
sleeping_time = int(getenv('SLEEPING_TIME'))
method_crawler = getenv('CRAWLER_METHOD')
schedule.every(sleeping_time).seconds.do(lambda: Crawler(method_crawler).crawl())

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    logging.info("Crawler started")
    while True:
        schedule.run_pending()
        sleep(1)
