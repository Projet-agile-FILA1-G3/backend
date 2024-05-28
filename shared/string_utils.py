import re
import ssl
from datetime import datetime

import nltk
from nltk.corpus import stopwords
from nltk.stem.snowball import SnowballStemmer

from db import get_session
from models.models import Token, Item, Rss

try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

nltk.download('stopwords')


class ProcessingString:
    def __init__(self, language='french'):
        self.language = language
        self.stopwords = set(stopwords.words(language))
        self.stemmer = SnowballStemmer(language)

    def remove_stopwords(self, sentence):
        return ' '.join([word for word in sentence.split() if word not in self.stopwords])

    def stem_word(self, word):
        return self.stemmer.stem(word)

    def process_text(self, text):
        text = text.lower()
        text = re.sub(r'[_\W]', ' ', text)
        text = self.remove_stopwords(text)
        return ' '.join([self.stem_word(word) for word in text.split()])