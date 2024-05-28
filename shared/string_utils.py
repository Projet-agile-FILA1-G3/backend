import re
import ssl

import nltk
from nltk.corpus import stopwords
from nltk.stem.snowball import SnowballStemmer

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
        text = re.sub(r'\b\d+\b', '', text)
        text = re.sub(r'[_\W]', ' ', text)
        text = self.remove_stopwords(text)
        tokens = [self.stem_word(word) for word in text.split()]
        tokens = [token for token in tokens if len(token) > 1]

        return ' '.join(tokens)
