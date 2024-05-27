import os
import uuid

from dotenv import load_dotenv
from sqlalchemy import Column, String, create_engine, UUID
from sqlalchemy.orm import declarative_base

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

    def __init__(self, url, description, title, last_fetching_date, **kw: any):
        super().__init__(**kw)
        self.url = url
        self.description = description
        self.title = title
        self.last_fetching_date = last_fetching_date

    def __str__(self):
        return f'{self.url} - {self.description} - {self.title} - {self.last_fetching_date}'


class RssItem(Base):
    __tablename__ = 'rss_item'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    link = Column(String, nullable=False)
    pub_date = Column(String, nullable=False)
    rss_id = Column(UUID(as_uuid=True), nullable=False)

    def __init__(self, title, description, link, pub_date, rss_id, **kw: any):
        super().__init__(**kw)
        self.title = title
        self.description = description
        self.link = link
        self.pub_date = pub_date
        self.rss_id = rss_id

    def __str__(self):
        return f'{self.title} - {self.description} - {self.link} - {self.pub_date} - {self.rss_id}'


if __name__ == '__main__':
    engine = create_engine(f'postgresql+psycopg2://{user}:{password}@{host}:{port}/{dbname}', echo=False)

    Base.metadata.create_all(engine)
