from enum import Enum
from re import sub

from nltk.corpus import stopwords
from nltk.stem.snowball import SnowballStemmer

alphabet = ([chr(i) for i in range(97, 123)] + ['é', 'è', 'à', 'ç', ' ', 'ï', 'ë', "'", 'ê', 'ô', 'œ', "'"]
            + [chr(i) for i in range(48, 59)])

stopwords = {
    'fr': set(stopwords.words('french')),
    'en': set(stopwords.words('english'))
}

stemmer = {
    'fr': SnowballStemmer('french'),
    'en': SnowballStemmer('english')
}


def get_tokens(string: str, language: str):
    return process_text(string, language)


def process_text(text, language):
    text = text.lower()
    try:
        text = extract_values(text)
    except:
        pass
    text = sub(r'\b\d+\b', '', text)
    text = sub(r'[_\W]', ' ', text)
    text = remove_stopwords(text, language)
    tokens = [stem_word(word, language) for word in text.split()]
    tokens = [token for token in tokens if len(token) > 1]
    return tokens


def extract_values(text):
    pattern_balise = r'<.*?>'
    pattern_back = r'[\a\b\f\n\r\t\v]'
    text = sub(pattern_balise, ' ', text)
    text = sub(pattern_back, '', text)
    text = text.replace('\xa0', ' ')
    text = text.replace('-', ' ')
    ret = ""
    for car in text:
        if car in alphabet:
            ret += car
        else:
            ret += ' '
    return ret


def remove_stopwords(sentence, language):
    return ' '.join([word for word in sentence.split() if word not in stopwords[language]])


def stem_word(word, language):
    return stemmer[language].stem(word)
