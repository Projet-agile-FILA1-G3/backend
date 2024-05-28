import hashlib

from requests import get
from rss_parser import RSSParser, BaseParser
from pandas import read_csv
from uuid import uuid4
from rss_parser.models.atom import Atom
from rss_parser.models.rss import RSS
from rss_parser.models.atom.feed import Tag, Entry
import rss_parser.models.rss.channel as RSS_tag
from re import sub

from shared.db import get_session
from shared.models import Rss, Item
from token_management import ProcessingToken

import datetime


# Si csv est choisi comme source, alors un fichier urls.csv doit se situer au même endroit que
# la classe Crawler.
#
#


class Crawler:
    alphabet = [chr(i) for i in range(97, 123)] + ['é', 'è', 'à', 'ç', ' ', 'ï', 'ë', "'", 'ê', 'ô', 'œ', "'"] + [chr(i)
                                                                                                                  for i
                                                                                                                  in
                                                                                                                  range(
                                                                                                                      48,
                                                                                                                      59)]

    @staticmethod
    def extract_values(text):

        text = text.lower()
        pattern_balise = r'<.*?>'
        pattern_back = r'[\a\b\f\n\r\t\v]'
        text = sub(pattern_balise, ' ', text)
        text = sub(pattern_back, '', text)
        text = text.replace('\xa0', ' ')
        text = text.replace('-', ' ')
        ret = ""
        for car in text:
            if car in Crawler.alphabet:
                ret += car
            else:
                ret += ' '
        return ret

    @staticmethod
    def split_content(text):
        return text.split("content='")[0].split("' attributes")[0]

    def __init__(self, RSS_URLS_TYPE='csv', STORAGE_TYPE='postgres'):
        self.source_type = RSS_URLS_TYPE.lower()
        self.storage_type = STORAGE_TYPE.lower()
        self.urls = self.get_URLs()

    def get_URLs(self):
        if self.source_type == 'csv':
            file = read_csv('./urls.csv')
            # print(file.iloc[:, 0].tolist())
            return file.iloc[:, 0].tolist()
        if self.source_type == 'postgres':
            # à développer
            pass
        if self.source_type == 'mangodb':
            # à développer
            pass

    def save_data(self, rss, items):
        # print(items[0]['source_url'], "\n\n\n\n")
        session = get_session()
        Object_rss = Rss(url=rss['url'], description=rss['description'] or "Pas de description",
                         title=rss['title'] or "Pas de titre",
                         last_fetching_date=rss['updated'] or datetime.datetime.now().isoformat())
        session.add(Object_rss)
        session.commit()
        rss_id = Object_rss.id
        for item in items:
            hashcode = hashlib.md5((item['title'] + item['description'] + item['url']).encode('utf-8')).hexdigest()

            existing_item = session.query(Item).filter_by(hashcode=hashcode).first()

            if existing_item:
                continue

            new_item = Item(title=item['title'], description=item['description'], link=item['url'],
                            pub_date=datetime.datetime.now(), rss_id=rss_id)
            session.add(new_item)
            session.commit()

            processing_token = ProcessingToken(rss['language'])
            tokens = processing_token.process_tokens(new_item.title, new_item.description, new_item.id)
            for token in tokens:
                # print(token)
                session.add(token)
            session.commit()

    def crawl(self):
        for urls in self.urls:
            items = []
            response = get(urls, headers={"User-Agent": "curl/7.64.1"})
            try:
                item_list = RSSParser.parse(response.text, schema=RSS).channel.items
                rss_info = RSSParser.parse(response.text, schema=RSS).channel
                # print(rss_info)
                rss_title = rss_info.title.content
                rss_language = rss_info.language.content
                rss_lastdate = None
                rss_description = None
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
                except Exception as error:
                    # print(response.url)
                    # print("Fatal Error :", error)
                    return 0
            try:
                if type(item_list[0]) == Tag[Entry]:
                    for item in item_list:
                        if item.content.content != None:
                            # print(item.content.links[0].attributes['href'])
                            items.append(dict({
                                'title': Crawler.extract_values(Crawler.split_content(item.content.title)),
                                'description': Crawler.extract_values(Crawler.split_content(item.content.content)),
                                'uuid': uuid4,
                                'source_url': response.url,
                                'url': item.content.links[0].attributes['href']
                            }))
                if type(item_list[0]) == RSS_tag.Tag[RSS_tag.Item]:
                    for item in item_list:
                        if item.description != None:
                            # print(Crawler.split_content(str(item.enclosure)))
                            # print(item.link.content)
                            items.append(dict({
                                'title': Crawler.extract_values(Crawler.split_content(item.title)),
                                'description': Crawler.extract_values(Crawler.split_content(item.description)),
                                'uuid': uuid4,
                                'source_url': response.url,
                                'url': item.link.content
                            }))
                        # indexation à faire ici

                # Enregistrement des données de la liste 'items' dans la DB ici
                self.save_data(rss_dict, items)
            except Exception as error:
                print("Fatal Error :", error)
                pass


if __name__ == '__main__':
    test = Crawler('csv').crawl()
