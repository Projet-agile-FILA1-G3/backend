import logging
import os

from dotenv import load_dotenv
from sqlalchemy.orm import declarative_base, Session, DeclarativeBase
from sqlalchemy import create_engine, Engine

from shared.models import Base


def get_db_config():
    return {
        'host': os.getenv('POSTGRES_HOST'),
        'port': os.getenv('POSTGRES_PORT'),
        'dbname': os.getenv('POSTGRES_DB'),
        'user': os.getenv('POSTGRES_USER'),
        'password': os.getenv('POSTGRES_PASSWORD')
    }


def get_db_url():
    db_config = get_db_config()
    return \
        f'postgresql+psycopg2://{db_config["user"]}:{db_config["password"]}@{db_config["host"]}:{db_config["port"]}/{db_config["dbname"]}'


def get_db_session():
    return engine.connect()


def get_session():
    return Session(engine)


if os.getenv('POSTGRES_HOST') is None:
    load_dotenv('../.env')

engine = create_engine(get_db_url())

# Required to create the tables
from shared.models.Feed import Feed
from shared.models.Item import Item
from shared.models.Token import Token

def init_db():
    Base.metadata.create_all(engine)
    logging.info("Database initialized")

