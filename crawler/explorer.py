import logging

import requests
from bs4 import BeautifulSoup
from shared.db import get_session
from shared.models import Rss, Item, Token
from datetime import datetime
import crawler_class

class Explorer:

    @staticmethod
    def transformUrl(url):
        return url.split('//')[1].split('/')[0]


    @staticmethod
    def save_link(link):
        try:
            session = get_session()
            rss_dict, _ = crawler_class.Crawler.process_page(link)
            session.add(Rss(link, rss_dict['description'], rss_dict['title'], datetime.now().isoformat()))
            session.commit()
            session.close()
            return 1
        except Exception as error:
            logging.error("Error while saving link %s : %s", link, error)
            return 0

    def get_links(self):
        soup = BeautifulSoup(self.response, 'html.parser')
        link_tags = soup.find_all('link')
        links = [link.get('href') for link in link_tags if (link.get('href') and link.get('type') == "application/rss+xml")]
        session = get_session()
        links_in_db = [url[0] for url in session.query(Rss.url).filter(Rss.url.in_(links)).all()]
        valid_links = list(set(links) - set(links_in_db))
        session.close()
        if len(valid_links) > 1:
            logging.info("Add those Rss to DB, they will be crawled next time : %s", valid_links)
            for link in valid_links:
                Explorer.save_link(link)
            return valid_links
        elif len(valid_links) == 1:
            logging.info("Add this Rss to DB, it will be crawled next time : %s", valid_links[0])
            Explorer.save_link(valid_links[0])
            return valid_links[0]
        else:
            return None

    def __init__(self, starturl, targeturl):
        self.starturl = Explorer.transformUrl(starturl)
        self.targeturl = Explorer.transformUrl(targeturl)
        self.next = None
        if self.targeturl != self.starturl:
            self.response = requests.get(targeturl, headers={"User-Agent": "curl/7.64.1"}).text
            self.next = self.get_links()

    def __str__(self):
        return self.next or ""
