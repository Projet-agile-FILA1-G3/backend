from datetime import datetime

from models.models import Rss, Item, Token
from shared.db import get_session
from shared.string_utils import ProcessingString
from collections import Counter


class ProcessingToken:
    def __init__(self, language='french'):
        self.processor = ProcessingString(language)

    def process_tokens(self, title, description, item_id):
        title_tokens = self.processor.process_text(title).split()
        description_tokens = self.processor.process_text(description).split()
        tokens = title_tokens + description_tokens
        word_counts = Counter(tokens)
        unique_tokens = set(tokens)
        return [Token(word=token, rank=word_counts[token], item_id=item_id) for token in unique_tokens]


if __name__ == '__main__':
    try:
        session = get_session()

        rss = Rss(url="http://example.com/rss", description="Example Description", title="Example Title",
                  last_fetching_date=datetime.now())
        session.add(rss)
        session.commit()

        item = Item(title="Bonjour voici un article", description="On a intervidhé ç!àé 3 00000 17/02/303 article", link="http://example.com",
                    pub_date=datetime.now(), rss_id=rss.id)
        session.add(item)
        session.commit()

        processing_token = ProcessingToken()

        tokens = processing_token.process_tokens(item.title, item.description, item.id)

        for token in tokens:
            print(token)
            session.add(token)

        session.commit()
        print("Tokens inserted!")
    except Exception as e:
        print(f"An error occurred: {e}")
