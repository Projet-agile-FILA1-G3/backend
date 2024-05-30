from requests import get
from rss_parser import RSSParser, BaseParser
from pandas import read_csv
from rss_parser.models.atom import Atom
from rss_parser.models.rss import RSS
from rss_parser.models.atom.feed import Tag, Entry
import rss_parser.models.rss.channel as RSS_tag

from sqlalchemy.exc import IntegrityError
from explorer import Explorer
from shared.db import get_session
from shared.models import Rss, Item
from token_management import ProcessingToken

from datetime import datetime, timedelta


class Crawler:

    @staticmethod
    def parse_date(date, protocol):
        if protocol.lower() == 'rss':
            if date.pub_date:
                date = date.pub_date.content
            else:
                return (datetime.now() - timedelta(days=2)).isoformat()
            try:
                return datetime.strptime(date, "%a, %d %b %Y %H:%M:%S %z").isoformat()
            except:
                return datetime.strptime(date, "%a, %d %b %Y %H:%M:%S %Z").isoformat()

        elif protocol.lower() == 'atom':
            if date.content.updated:
                return date.content.updated.content.isoformat()
            else:
                return (datetime.now() - timedelta(days=2)).isoformat()

    @staticmethod
    def split_content(text):
        return text.split("content='")[0].split("' attributes")[0]

    @staticmethod
    def process_page(url, headers="curl/7.64.1"):
        response = get(url, headers={"User-Agent": headers})
        try:
            item_list = RSSParser.parse(response.text, schema=RSS).channel.items
            rss_info = RSSParser.parse(response.text, schema=RSS).channel
            rss_title = rss_info.title.content
            rss_language = rss_info.language.content
            rss_url = response.url
            try:
                rss_description = rss_info.description.content
            except:
                rss_description = None
            try:
                rss_lastdate = rss_info.pub_date.content.isoformat()
            except:
                try:
                    rss_lastdate = rss_info.last_build_date.isoformat()
                except:
                    rss_lastdate = None
            rss_dict = dict({
                'language': rss_language,
                'title': rss_title,
                'updated': rss_lastdate,
                'url': rss_url,
                'description': rss_description
            })
            return rss_dict, item_list
        except Exception as primeError:
            # print("Attention erreur ici :", primeError)
            try:
                item_list = BaseParser.parse(response.text, schema=Atom).feed.content.entries
                atom_info = BaseParser.parse(response.text, schema=Atom).feed.content
                atom_language = 'en'
                atom_title = atom_info.title.content
                atom_updated = atom_info.updated.content
                atom_url = response.url
                rss_dict = dict({
                    'language': atom_language,
                    'title': atom_title,
                    'updated': atom_updated,
                    'url': atom_url,
                    'description': None
                })
                return rss_dict, item_list
            except Exception as error:
                return None, []


    @staticmethod
    def process_items(item_list, url):
        items = []
        try:
            if type(item_list[0]) == Tag[Entry]:
                for item in item_list:
                    if item.content.content != None:
                        items.append(dict({
                            'title': Crawler.split_content(item.content.title),
                            'description': Crawler.split_content(item.content.content),
                            'source_url': url,
                            'url': item.content.links[0].attributes['href'],
                            'pub_date': Crawler.parse_date(item, 'atom')
                        }))
                        Explorer(url, item.content.links[0].attributes['href'])
                return items
            if type(item_list[0]) == RSS_tag.Tag[RSS_tag.Item]:
                for item in item_list:
                    if item.description != None:
                        items.append(dict({
                            'title': Crawler.split_content(item.title),
                            'description': Crawler.split_content(item.description),
                            'source_url': url,
                            'url': item.link.content,
                            'pub_date': Crawler.parse_date(item, 'rss')
                        }))
                        Explorer(url, item.link.content)
                return items
        except Exception as error:
            print("Fatal Error :", error)
            return []

    def __init__(self, RSS_URLS_TYPE = 'csv', STORAGE_TYPE = 'postgres', DEF_URL = None):
        self.source_type = RSS_URLS_TYPE.lower()
        self.storage_type = STORAGE_TYPE.lower()
        if DEF_URL != None:
            self.urls = DEF_URL
        else:
            self.urls = self.get_URLs()

    def get_URLs(self):
        if self.source_type == 'csv' or self.source_type != 'db':
            file = read_csv('./urls.csv')
            # print(file.iloc[:, 0].tolist())
            return file.iloc[:, 0].tolist()
        else:
            session = get_session()
            res = [url[0] for url in session.query(Rss.url).all()]
            session.close()
            return res

    def save_data(self, rss, items):
        # print(items[0]['source_url'], "\n\n\n\n")
        session = get_session()
        Object_rss = session.query(Rss).filter_by(url=rss['url']).first()

        if Object_rss:
            Object_rss.description = rss['description'] or "Pas de description"
            Object_rss.title = rss['title'] or "Pas de titre"
            Object_rss.last_fetching_date = rss['updated'] or datetime.now().isoformat()
            rss_id = Object_rss.id
        else:
            Object_rss = Rss(url=rss['url'], description=rss['description'] or "Pas de description",
                             title=rss['title'] or "Pas de titre",
                             last_fetching_date=rss['updated'] or datetime.now().isoformat())
            session.add(Object_rss)
            session.commit()
            rss_id = Object_rss.id

        try:
            session.commit()
        except IntegrityError:
            session.rollback()

        for item in items:
            item_obj = Item(title=item['title'], description=item['description'], link=item['url'],
                            pub_date=datetime.now(), rss_id=rss_id)
            try:
                session.add(item_obj)
                session.commit()
                item_id = item_obj.hashcode
            except IntegrityError:
                session.rollback()
                existing_item = session.query(Item).filter_by(
                    title=item['title'], description=item['description'], link=item['url'], rss_id=rss_id
                ).first()
                if existing_item:
                    item_id = existing_item.hashcode
                else:
                    raise Exception("Failed to retrieve or insert Item record.")

            processing_token = ProcessingToken(rss['language'])
            tokens = processing_token.process_tokens(item["title"], item["description"], item_id)
            for token in tokens:
                try:
                    session.add(token)
                    session.commit()
                except IntegrityError:
                    session.rollback()
                    continue
        session.close()

    def crawl(self):
        for url in self.urls:
            rss_dict, item_list = Crawler.process_page(url)
            items = Crawler.process_items(item_list, url)
            self.save_data(rss_dict, items)

if __name__ == '__main__':
    Crawler().crawl()
