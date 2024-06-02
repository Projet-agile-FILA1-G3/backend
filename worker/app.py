import logging
from queue import Queue
from threading import Thread

from worker.crawler import crawler
from worker.scheduler import scheduler

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    logging.getLogger().setLevel(logging.DEBUG)
    logging.info("Starting worker")

    fifo = Queue()

    Thread(target=crawler, args=(fifo,), daemon=True).start()

    Thread(target=scheduler, args=(fifo,), daemon=True).start()

    while True:
        pass

