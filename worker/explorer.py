import requests
from bs4 import BeautifulSoup

from shared.db import get_session
from shared.models import Feed
from worker.crawler import crawler, crawl_feed


# These functions are used to explore a website to find a new rss feed on it.

def explore(link):
    link = transform_url(link)
    response = requests.get(link, headers={"User-Agent": "curl/7.64.1"}).text
    new_links = extract_links(response)
    for new_link in new_links:
        feed = crawl_feed(new_link, with_items=False)
        session = get_session()
        Feed.insert(session, feed)
        session.commit()
        session.close()


def transform_url(url):
    return url.split('//')[1].split('/')[0]


def extract_links(response):
    soup = BeautifulSoup(response, 'html.parser')
    link_tags = soup.find_all('link')
    links = [link.get('href') for link in link_tags if (link.get('href') and link.get('type') == "application/rss+xml")]
    valid_links = get_not_saved_links(links)

    return valid_links


def get_not_saved_links(links):
    session = get_session()
    saved_feeds = Feed.find_all(session)
    links_in_db = [url[0] for url in saved_feeds]
    valid_links = list(set(links) - set(links_in_db))
    session.close()
    return valid_links
