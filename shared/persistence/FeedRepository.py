from datetime import datetime

from sqlalchemy.orm import Session

from shared.models.Feed import Feed


class FeedRepository:

    def __init__(self, session : Session):
        self.session = session

    def find_all(self) -> [Feed]:
        return self.session.query(Feed).all()

    def count(self) -> int:
        return self.session.query(Feed).count()

    def find_by_id(self, feed_id) -> Feed or None:
        return self.session.query(Feed).filter(Feed.id == feed_id).first()

    def find_by_url(self, url) -> Feed or None:
        return self.session.query(Feed).filter(Feed.url == url).first()

    def exists_url(self, url) -> bool:
        return self.session.query(Feed).filter(Feed.url == url).count() > 0

    def store(self, feed) -> None:
        self.session.add(feed)
        self.session.commit()

    def update_last_fetching_date(self, feed_id):
        feed = self.find_by_id(feed_id)
        feed.last_fetching_date = datetime.now()
        self.session.commit()

    def find_last_fetched(self):
        return self.session.query(Feed).order_by(Feed.last_fetching_date.desc()).first()


