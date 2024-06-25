import logging

from shared.models.Item import Item


class ItemRepository:
    def __init__(self, session):
        self.session = session

    def find_all(self) -> [Item]:
        return self.session.query(Item).all()

    def find_by_hashcode(self, item_hashcode) -> Item:
        return self.session.query(Item).filter(Item.hashcode == item_hashcode).first()

    def find_by_feed_id(self, feed_id) -> [Item]:
        return self.session.query(Item).filter(Item.feed_id == feed_id).all()

    def exists(self, item) -> bool:
        return self.session.query(Item).filter(Item.hashcode == item.hashcode).count() > 0

    def store(self, item) -> None:
        self.session.add(item)
        self.session.commit()
