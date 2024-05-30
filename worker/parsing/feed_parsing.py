from abc import ABC, abstractmethod

from rss_parser import RSSParser
from rss_parser.models.atom import Atom
from rss_parser.models.rss import RSS

from worker.parsing.item_parsing import RssItemParsing, AtomItemParsing
from shared.models.Feed import Feed
from shared.models.Item import Item


# Abstract class
class FeedParser(ABC):

    def __init__(self, raw_feed: str, url: str, feed_id: int = None):
        self.raw_feed = raw_feed
        self.url = url
        self.feed_id = feed_id

    def parse(self) -> Feed:
        feed = Feed(
            url=self.url,
            description=self.get_description(),
            title=self.get_title(),
            last_fetching_date=self.get_last_fetching_date()
        )
        feed.items = self.parse_items()
        return feed

    def parse_items(self) -> list[Item]:
        return [self.parse_item(raw_item) for raw_item in self.get_raw_items()]

    @abstractmethod
    def parse_item(self, raw_item: any) -> Item:
        pass

    @abstractmethod
    def get_title(self) -> str:
        pass

    @abstractmethod
    def get_description(self) -> str:
        pass

    @abstractmethod
    def get_last_fetching_date(self) -> str:
        pass

    @abstractmethod
    def get_raw_items(self) -> list[any]:
        pass


class RssFeedParser(FeedParser):

    def __init__(self, raw_feed: str, url: str, feed_id: int = None):
        super().__init__(raw_feed, url, feed_id)
        self.parsed_feed = RSSParser.parse(raw_feed, schema=RSS)

    def parse_item(self, raw_item: any) -> Item:
        return RssItemParsing(raw_item, self.feed_id).parse()

    def get_title(self) -> str:
        return self.parsed_feed.channel.title.content

    def get_description(self) -> str or None:
        if self.parsed_feed.channel.description:
            return self.parsed_feed.channel.description.content
        return None

    def get_last_fetching_date(self) -> str or None:
        if self.parsed_feed.channel.pub_date:
            return self.parsed_feed.channel.pub_date.content.isoformat()
        if self.parsed_feed.channel.last_build_date:
            return self.parsed_feed.channel.last_build_date.isoformat()
        return None

    def get_raw_items(self) -> list[any]:
        return self.parsed_feed.channel.items


class AtomFeedParser(FeedParser):

    def __init__(self, raw_feed: str, url: str, feed_id: int = None):
        super().__init__(raw_feed, url, feed_id)
        self.parsed_feed = RSSParser.parse(raw_feed, schema=Atom)

    def parse_item(self, raw_item: any) -> Item:
        return AtomItemParsing(raw_item, self.feed_id).parse()

    def get_title(self) -> str:
        return self.parsed_feed.feed.content.title.content

    def get_description(self) -> str or None:
        return None

    def get_last_fetching_date(self) -> str:
        return self.parsed_feed.feed.content.updated.content

    def get_raw_items(self) -> list[any]:
        return self.parsed_feed.feed.content.entries
