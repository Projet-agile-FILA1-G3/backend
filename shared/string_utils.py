from nltk.corpus import stopwords
from nltk.stem.snowball import SnowballStemmer

LANGUAGE = 'french'

stopwords = set(stopwords.words(LANGUAGE))
stemmer = SnowballStemmer(LANGUAGE)


def remove_stopwords(sentence):
    return ' '.join([word for word in sentence.split() if word not in stopwords])


def stem_word(word):
    return stemmer.stem(word)


if __name__ == '__main__':
    string = "J'ai eu une très mauvaise expérience avec ce produit. Je ne le recommande pas."
    string = string.lower()
    string = remove_stopwords(string)
    print(string)
    for w in string.split():
        print(stem_word(w))
