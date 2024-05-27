from requests import get
from rss_parser import RSSParser
from pandas import read_csv
from uuid import uuid4

# Si csv est choisi comme source, alors un fichier urls.csv doit se situer au même endroit que
# la classe Crawler.
#
#

class Crawler:
    alphabet = [chr(i) for i in range(97, 123)] + ['é', 'è', 'à', 'ç', ' ', 'ï', 'ë', "'", 'ê', 'ô', 'œ'] + [chr(i) for i in range(48, 59)]

    @staticmethod
    def extract_values(text):
        text = text.lower()
        text = text.replace('\xa0', ' ')
        text = text.replace('-', ' ')
        ret = ""
        for car in text:
            if car in Crawler.alphabet:
                ret += car
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
        pass

    def crawl(self):
        for urls in self.urls:
            items = []
            response = get(urls,  headers={"User-Agent": "curl/7.64.1"})
            for item in RSSParser.parse(response.text).channel.items:
                if item.description != None:

                    items.append(dict({
                        'title': Crawler.extract_values(Crawler.split_content(item.title)),
                        'description': Crawler.extract_values(Crawler.split_content(item.description)),
                        'uuid': uuid4
                    }))
                    # indexation à faire ici

            # Enregistrement des données de la liste 'items' dans la DB ici
            self.save_data(items)

test = Crawler('csv').crawl()