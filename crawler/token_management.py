from datetime import datetime

from models.models import Rss, Item, Token
from shared.db import get_session
from shared.string_utils import ProcessingString


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
