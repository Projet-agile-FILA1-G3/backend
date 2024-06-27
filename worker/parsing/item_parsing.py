import logging
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from shared.models.Item import Item
import html

def split_content(text):
    text = text.split("content='")[0].split("' attributes")[0]
    return text
    """
    try:
        decoded_text = BeautifulSoup(text).getText()
        picture_link = BeautifulSoup(text).find('picture')['src']
        return decoded_text, picture_link
    except:
        return text"""

class ItemParser(ABC):
    def __init__(self, parsed_item, feed_id):
        self.item = parsed_item
        self.feed_id = feed_id

    def parse(self):
        item = Item(
            title=self.get_title(),
            description=self.get_description(),
            link=self.get_link(),
            pub_date=self.get_pub_date(),
            feed_id=self.feed_id,
            audio_link=self.get_audio(),
            image_link=self.get_image()
        )
        return item

    @abstractmethod
    def get_title(self):
        pass

    @abstractmethod
    def get_description(self):
        pass

    @abstractmethod
    def get_link(self):
        pass

    @abstractmethod
    def get_audio(self):
        pass

    @abstractmethod
    def get_image(self):
        pass

    def get_pub_date(self):
        return (datetime.now() - timedelta(days=2)).isoformat()


class RssItemParser(ItemParser):

    def __init__(self, parsed_item, feed_id):
        super().__init__(parsed_item, feed_id)

    def get_title(self):
        return split_content(self.item.title)

    def get_description(self):
        if not self.item.description:
            raise Exception("No description")
        content = split_content(self.item.description)
        try:
            decoded_text = BeautifulSoup(content).getText()
            return decoded_text
        except:
            return content

    def get_link(self):
        try:
            return self.item.link.content
        except:
            return self.get_audio()

    def get_audio(self):
        try:
            if self.item.enclosure.attributes['type'] == 'audio/mpeg':
                return self.item.enclosure.attributes['url']
        except:
            return None

    def get_image(self):
        try:
            picture_link = None
            if BeautifulSoup(html.unescape(split_content(self.item.description)), features='html.parser').find('picture'):
                picture_link = BeautifulSoup(html.unescape(split_content(self.item.description)), features='html.parser').find('picture')['src']
            if BeautifulSoup(html.unescape(split_content(self.item.description)), features='html.parser').find('img'):
                picture_link = BeautifulSoup(html.unescape(split_content(self.item.description)), features='html.parser').find('img')['src']
            return picture_link
        except:
            return None

    def get_pub_date(self):
        if not self.item.pub_date:
            return super().get_pub_date()
        date = self.item.pub_date.content
        # TODO: WHAT IS IT ?
        try:
            return datetime.strptime(date, "%a, %d %b %Y %H:%M:%S %z").isoformat()
        except:
            return datetime.strptime(date, "%a, %d %b %Y %H:%M:%S %Z").isoformat()


class AtomItemParser(ItemParser):

    def __init__(self, parsed_item, feed_id):
        super().__init__(parsed_item, feed_id)

    def get_title(self):
        return split_content(self.item.content.title)

    def get_description(self):
        content = split_content(self.item.content.content)
        try:
            decoded_text = BeautifulSoup(content).getText()
            return decoded_text
        except:
            return content

    def get_link(self):
        return self.item.content.links[0].attributes['href']

    def get_audio(self):
        # TODO : Il faut que l'on teste avec du atom et du podcast
        return None

    def get_image(self):
        try:
            picture_link = None
            if BeautifulSoup(html.unescape(split_content(self.item.content.content)), features='html.parser').find('picture'):
                picture_link = BeautifulSoup(html.unescape(split_content(self.item.content.content)), features='html.parser').find('picture')['src']
            if BeautifulSoup(html.unescape(split_content(self.item.content.content)), features='html.parser').find('img'):
                picture_link = BeautifulSoup(html.unescape(split_content(self.item.content.content)), features='html.parser').find('img')['src']
            return picture_link
        except:
            return None

    def get_pub_date(self):
        if not self.item.content.updated:
            return super().get_pub_date()
        return self.item.content.updated.content.isoformat()
