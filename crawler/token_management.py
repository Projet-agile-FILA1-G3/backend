from shared.models import Token
from shared.string_utils import ProcessingString
from collections import Counter


class ProcessingToken:
    def __init__(self, language='french'):
        self.processor = ProcessingString(language)

    def process_tokens(self, title, description, item_id):
        title_tokens = self.processor.process_text(title).split()
        description_tokens = self.processor.process_text(description).split()
        word_counts = Counter()

        for token in title_tokens:
            word_counts[token] += 3

        for token in description_tokens:
            word_counts[token] += 1

        return [Token(word=token, rank=word_counts[token], item_id=item_id) for token in set(title_tokens + description_tokens)]

