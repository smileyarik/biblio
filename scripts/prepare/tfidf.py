from collections import Counter
import string
import os

import razdel
import nltk
from nltk.stem.snowball import SnowballStemmer
from nltk.corpus import stopwords

punct_translator = str.maketrans(string.punctuation, " " * len(string.punctuation))
stemmer = SnowballStemmer("russian")

nltk.download("stopwords")
stopwords = set(stopwords.words("russian"))


def tokenize_to_lemmas(text):
    text = str(text).strip().replace("\n", " ").replace("\xa0", " ")
    text = text.lower()
    text = text.translate(punct_translator)
    text = " ".join(text.split())
    tokens = [t.text for t in razdel.tokenize(text)]
    tokens = [t for t in tokens if t not in stopwords]
    tokens = [stemmer.stem(t) for t in tokens]
    tokens = [t for t in tokens if not t.isnumeric()]
    tokens = [t for t in tokens if len(t) >= 2]
    return tokens


def get_keywords(text, word2idf, word2idx, k=10):
    if not text:
        return []
    tokens = tokenize_to_lemmas(text)
    if not tokens:
        return []
    freqs = Counter(tokens)
    tfs = {token: float(f) / len(tokens) for token, f in freqs.items()}
    data = []
    for token, tf in tfs.items():
        if idf := word2idf.get(token, None):
            idf = word2idf.get(token, 0.0)
            tfidf = tf * idf
            data.append((tfidf, word2idx[token]))
    data.sort(reverse=True)
    return [t for _, t in data[:k]]


def load_idfs(file_name):
    assert os.path.exists(file_name)
    word2idf, word2idx = dict(), dict()
    with open(file_name, "r") as r:
        for idx, line in enumerate(r):
            word, idf = line.strip().split("\t")
            word2idf[word] = float(idf)
            word2idx[word] = int(idx)
    return word2idf, word2idx
