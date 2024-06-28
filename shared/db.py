import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from shared.models import Base

if os.getenv('NODE_MODE') != 'production':
    load_dotenv('.env')

host = os.getenv('POSTGRES_HOST')
port = os.getenv('POSTGRES_PORT')
dbname = os.getenv('POSTGRES_DB')
user = os.getenv('POSTGRES_USER')
password = os.getenv('POSTGRES_PASSWORD')

DATABASE_URL = f'postgresql+psycopg2://{user}:{password}@{host}:{port}/{dbname}'

engine = create_engine(DATABASE_URL, echo=False)
Session = sessionmaker(bind=engine)


def get_session():
    return Session()


if __name__ == '__main__':
    try:
        Base.metadata.create_all(engine)
        print("Tables created!")
    except Exception as e:
        print(f"An error occurred: {e}")