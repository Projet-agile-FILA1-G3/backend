import logging
from collections import Counter

from shared.db import get_session
from shared.models.Item import Item
from shared.models import Token
from shared.persistence.TokenRepository import TokenRepository
from shared.tokenizer import process_text, get_tokens

session = get_session()
tokenRepository = TokenRepository(session)


def index_item(item: Item):
    logging.info(f'Indexing item {item.hashcode}')

    # Indexing
    title_tokens = get_tokens(item.title)
    description_tokens = get_tokens(item.description)
    word_counts = Counter()

    # Ranking
    for token in title_tokens:
        word_counts[token] += 3

    for token in description_tokens:
        word_counts[token] += 1

    tokens = [Token.Token(word=token, rank=word_counts[token], item_id=item.hashcode) \
              for token in set(title_tokens + description_tokens)]

    for token in tokens:
        tokenRepository.store(token)
    logging.info(f'Indexed item {item.hashcode}')
