import csv
import os

from shared.db import get_session
from shared.models.Feed import Feed
from shared.persistence.FeedRepository import FeedRepository


def is_prod_env():
    return os.getenv('ENV') == 'production'


def add_defaults_feed():
    feed_repo = FeedRepository(get_session())
    if len(feed_repo.find_all()) == 0:
        with open('urls.csv', 'r') as file:
            reader = csv.reader(file)
            for row in reader:
                url, lang = row
                new_feed = Feed(url=url, description='', title='', last_fetching_date='', lang=lang)
                feed_repo.store(new_feed)
