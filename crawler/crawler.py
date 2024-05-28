from requests import get
from rss_parser import RSSParser, BaseParser
from pandas import read_csv
from uuid import uuid4
from rss_parser.models.atom import Atom
from rss_parser.models.rss import RSS
from rss_parser.models.atom.feed import Tag, Entry
import rss_parser.models.rss.channel as RSS_tag
from re import sub

# Si csv est choisi comme source, alors un fichier urls.csv doit se situer au même endroit que
# la classe Crawler.
# 
#

class Crawler:
    alphabet = [chr(i) for i in range(97, 123)] + ['é', 'è', 'à', 'ç', ' ', 'ï', 'ë', "'", 'ê', 'ô', 'œ', "'"] + [chr(i) for i in range(48, 59)]

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

    def __init__(self, RSS_URLS_TYPE = 'csv', STORAGE_TYPE = 'postgres'):
        self.source_type = RSS_URLS_TYPE.lower()
        self.storage_type = STORAGE_TYPE.lower()
        self.urls = self.get_URLs()

    def get_URLs(self):
        if self.source_type == 'csv':
            file = read_csv('./urls.csv')
            print(file.iloc[:, 0].tolist())
            return file.iloc[:, 0].tolist()
        if self.source_type == 'postgres':
            # à développer
            pass
        if self.source_type == 'mangodb':
            # à développer
            pass

    def save_data(self, items):
        print("\n\n\n\n", items[0]['source_url'])
        for item in items:
            #print(item['description'])
            pass

    def crawl(self):
        for urls in self.urls:
            items = []
            response = get(urls,  headers={"User-Agent": "curl/7.64.1"})
            try:
                item_list = RSSParser.parse(response.text, schema=RSS).channel.items
            except Exception as primeError:
                # print(primeError)
                try:
                    item_list = BaseParser.parse(response.text, schema=Atom).feed.content.entries
                    #print("type of item_list :", type(item_list.content.entries),"\nItem_list non formatté :", item_list.content.entries, "\ninfo :", item_list.__dict__)
                except Exception as error:
                    print(response.url)
                    print("Fatal Error :", error)
                    return 0

            try:
                if type(item_list[0]) == Tag[Entry] :
                    for item in item_list:
                        if item.content.content != None:
                            print(item.content.link)
                            items.append(dict({
                                'title': Crawler.extract_values(Crawler.split_content(item.content.title)),
                                'description': Crawler.extract_values(Crawler.split_content(item.content.content)),
                                'uuid': uuid4,
                                'source_url': response.url
                                #'image': item.content.image
                            }))
                if type(item_list[0]) == RSS_tag.Tag[RSS_tag.Item]:
                    for item in item_list:
                        if item.description != None:
                            #print(Crawler.split_content(str(item.enclosure)))
                            print(item.link)
                            items.append(dict({
                                'title': Crawler.extract_values(Crawler.split_content(item.title)),
                                'description': Crawler.extract_values(Crawler.split_content(item.description)),
                                'uuid': uuid4,
                                'source_url': response.url
                                #'image': item.image
                            }))
                        # indexation à faire ici

                # Enregistrement des données de la liste 'items' dans la DB ici
                self.save_data(items)
            except Exception as error:
                print("Fatal Error :", error)
                pass

test = Crawler('csv').crawl()