import logging
from abc import ABC, abstractmethod

import requests
from rss_parser import RSSParser
from rss_parser.models.atom import Atom
from rss_parser.models.rss import RSS

from shared.exception import FetchingException, ParsingException
from worker.parsing.item_parsing import RssItemParser, AtomItemParser
from shared.models.Feed import Feed
from shared.models.Item import Item


def crawl_feed(feed: Feed, with_items: bool = True) -> Feed:
    raw_feed = fetch_full_raw_feed(feed.url)
    try:
        feed = RssFeedParser(raw_feed, url=feed.url, feed_id=feed.id).parse(with_items=with_items)
    except Exception as e:
        try:
            feed = AtomFeedParser(raw_feed, url=feed.url, feed_id=feed.id).parse(with_items=with_items)
        except Exception as e:
            logging.debug(f'Failed to parse body as RSS or Atom: {raw_feed}', exc_info=True)
            logging.debug(f'Failed to parse feed {feed.url}: {e}', exc_info=True)
            raise ParsingException(f'Failed to parse feed {feed.url}: {e}')
    return feed


def fetch_full_raw_feed(feed_url : str) -> str:
    response = requests.get(feed_url, headers={"User-Agent": "curl/7.64.1"})
    if response.status_code != 200:
        raise FetchingException(f'Failed to fetch feed {feed_url}, status code {response.status_code}')
    return response.text


# Abstract class
class FeedParser(ABC):

    def __init__(self, raw_feed: str, url: str, feed_id: int = None):
        self.raw_feed = raw_feed
        if not raw_feed:
            self.raw_feed = requests.get(url).text
        self.url = url
        self.feed_id = feed_id

    def parse(self, with_items: bool = True) -> Feed:
        feed = Feed(
            url=self.url,
            description=self.get_description(),
            title=self.get_title(),
            last_fetching_date=self.get_last_fetching_date(),
            lang=self.get_lang()
        )
        if with_items:
            feed.items = self.parse_items()
        return feed

    def parse_items(self) -> list[Item]:
        items = []
        for raw_item in self.get_raw_items():
            try:
                item = self.parse_item(raw_item)
                items.append(item)
            except Exception as e:
                logging.error(f'Error while parsing item: {e}')
                logging.debug(f'Error while parsing item: {e}', exc_info=True)
        return items

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

    @abstractmethod
    def get_lang(self) -> str or None:
        pass


class RssFeedParser(FeedParser):

    def __init__(self, raw_feed: str, url: str, feed_id: int = None):
        super().__init__(raw_feed, url, feed_id)
        self.parsed_feed = RSSParser.parse(raw_feed, schema=RSS)

    def parse_item(self, raw_item: any) -> Item:
        return RssItemParser(raw_item, self.feed_id).parse()

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

    def get_lang(self) -> str or None:
        if self.parsed_feed.channel.language:
            return self.parsed_feed.channel.language.content
        return None


class AtomFeedParser(FeedParser):

    def __init__(self, raw_feed: str, url: str, feed_id: int = None):
        super().__init__(raw_feed, url, feed_id)
        self.parsed_feed = RSSParser.parse(raw_feed, schema=Atom)

    def parse_item(self, raw_item: any) -> Item:
        return AtomItemParser(raw_item, self.feed_id).parse()

    def get_title(self) -> str:
        return self.parsed_feed.feed.content.title.content

    def get_description(self) -> str or None:
        return None

    def get_last_fetching_date(self) -> str:
        return self.parsed_feed.feed.content.updated.content

    def get_raw_items(self) -> list[any]:
        return self.parsed_feed.feed.content.entries

    def get_lang(self) -> str or None:
        # TODO : find a way to get the language from the feed
        pass
