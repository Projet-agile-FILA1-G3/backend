from abc import ABC, abstractmethod
from datetime import datetime, timedelta

from shared.models.Item import Item


def split_content(text):
    return text.split("content='")[0].split("' attributes")[0]


class ItemParsing(ABC):
    def __init__(self, parsed_item, feed_id):
        self.item = parsed_item
        self.feed_id = feed_id

    def parse(self):
        item = Item(
            title=self.get_title(),
            description=self.get_description(),
            link=self.get_link(),
            pub_date=self.get_pub_date(),
            feed_id=self.feed_id
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

    def get_pub_date(self):
        return (datetime.now() - timedelta(days=2)).isoformat()


class RssItemParsing(ItemParsing):

    def __init__(self, parsed_item, feed_id):
        super().__init__(parsed_item, feed_id)

    def get_title(self):
        return split_content(self.item.title)

    def get_description(self):
        if not self.item.description:
            raise Exception("No description")
        return split_content(self.item.description)

    def get_link(self):
        return self.item.link.content

    def get_pub_date(self):
        if not self.item.pub_date:
            return super().get_pub_date()
        date = self.item.pub_date.content
        # TODO: WHAT IS IT ?
        try:
            return datetime.strptime(date, "%a, %d %b %Y %H:%M:%S %z").isoformat()
        except:
            return datetime.strptime(date, "%a, %d %b %Y %H:%M:%S %Z").isoformat()


class AtomItemParsing(ItemParsing):

    def __init__(self, parsed_item, feed_id):
        super().__init__(parsed_item, feed_id)

    def get_title(self):
        return split_content(self.item.content.title)

    def get_description(self):
        return split_content(self.item.content.content)

    def get_link(self):
        return self.item.content.links[0].attributes['href']

    def get_pub_date(self):
        if not self.item.content.updated:
            return super().get_pub_date()
        return self.item.content.updated.content.isoformat()
