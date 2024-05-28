import os
import uuid

from dotenv import load_dotenv
from sqlalchemy import Column, String, UUID, DateTime, ForeignKey, PrimaryKeyConstraint, Integer
from sqlalchemy.orm import declarative_base, relationship

load_dotenv('.env')

host = os.getenv('POSTGRES_HOST')
port = os.getenv('POSTGRES_PORT')
dbname = os.getenv('POSTGRES_DB')
user = os.getenv('POSTGRES_USER')
password = os.getenv('POSTGRES_PASSWORD')

Base = declarative_base()


class Rss(Base):
    __tablename__ = 'rss'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    url = Column(String, nullable=False)
    description = Column(String, nullable=False)
    title = Column(String, nullable=False)
    last_fetching_date = Column(String, nullable=False)

    items = relationship("Item", back_populates="rss", cascade="all, delete-orphan")

    def __init__(self, url, description, title, last_fetching_date, **kw: any):
        super().__init__(**kw)
        self.url = url
        self.description = description
        self.title = title
        self.last_fetching_date = last_fetching_date

    def __str__(self):
        return (f'Rss(\n'
                f'  id={self.id},\n'
                f'  url="{self.url}",\n'
                f'  description="{self.description}",\n'
                f'  title="{self.title}",\n'
                f'  last_fetching_date="{self.last_fetching_date}"\n'
                f')')


class Item(Base):
    __tablename__ = 'item'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    link = Column(String, nullable=False)
    pub_date = Column(DateTime, nullable=False)
    hashcode = Column(String, nullable=False)
    rss_id = Column(UUID(as_uuid=True), ForeignKey('rss.id'), nullable=False)

    rss = relationship("Rss", back_populates="items")

    tokens = relationship("Token", back_populates="item", cascade="all, delete-orphan")

    def __init__(self, title, description, link, pub_date, rss_id, **kw):
        super().__init__(**kw)
        self.title = title
        self.description = description
        self.link = link
        self.pub_date = pub_date
        self.hashcode = hash(f'{title}{description}{link}{pub_date}')
        self.rss_id = rss_id

    def __str__(self):
        return (f'Item(\n'
                f'  id={self.id},\n'
                f'  title="{self.title}",\n'
                f'  description="{self.description}",\n'
                f'  link="{self.link}",\n'
                f'  pub_date="{self.pub_date}",\n'
                f'  rss_id={self.rss_id}\n'
                f')')


class Token(Base):
    __tablename__ = 'token'
    word = Column(String, primary_key=True)
    rank = Column(Integer, nullable=False)
    item_id = Column(UUID(as_uuid=True), ForeignKey('item.id'), primary_key=True)

    item = relationship("Item", back_populates="tokens")

    __table_args__ = (
        PrimaryKeyConstraint('word', 'item_id', name='token_pk'),
    )

    def __init__(self, word, rank, item_id, **kw):
        super().__init__(**kw)
        self.word = word
        self.rank = rank
        self.item_id = item_id

    def __str__(self):
        return (f'Token(\n'
                f'  word="{self.word}",\n'
                f'  rank={self.rank},\n'
                f'  item_id={self.item_id}\n'
                f')')
