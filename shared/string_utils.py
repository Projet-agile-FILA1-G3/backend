from re import sub
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
    alphabet = [chr(i) for i in range(97, 123)] + ['é', 'è', 'à', 'ç', ' ', 'ï', 'ë', "'", 'ê', 'ô', 'œ', "'"] + [chr(i)
                                                                                                                  for i
                                                                                                                  in
                                                                                                                  range(
                                                                                                                      48,
                                                                                                                      59)]

    @staticmethod
    def extract_values(text):
        pattern_balise = r'<.*?>'
        pattern_back = r'[\a\b\f\n\r\t\v]'
        text = sub(pattern_balise, ' ', text)
        text = sub(pattern_back, '', text)
        text = text.replace('\xa0', ' ')
        text = text.replace('-', ' ')
        ret = ""
        for car in text:
            if car in ProcessingString.alphabet:
                ret += car
            else:
                ret += ' '
        return ret

    def __init__(self, in_language='french'):
        if in_language == 'fr':
            self.language = 'french'
        elif in_language == 'en':
            self.language = 'english'
        else:
            self.language = 'french'
        self.stopwords = set(stopwords.words(self.language))
        self.stemmer = SnowballStemmer(self.language)

    def remove_stopwords(self, sentence):
        return ' '.join([word for word in sentence.split() if word not in self.stopwords])

    def stem_word(self, word):
        return self.stemmer.stem(word)

    def process_text(self, text):
        text = text.lower()
        try:
            text = ProcessingString.extract_values(text)
        except:
            pass
        text = sub(r'\b\d+\b', '', text)
        text = sub(r'[_\W]', ' ', text)
        text = self.remove_stopwords(text)
        tokens = [self.stem_word(word) for word in text.split()]
        tokens = [token for token in tokens if len(token) > 1]
        return ' '.join(tokens)
