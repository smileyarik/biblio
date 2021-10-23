from collections import Counter
import string

from pyonmttok import Tokenizer
from pymorphy2 import MorphAnalyzer


tokenizer = Tokenizer("conservative", joiner_annotate=False)
morph = MorphAnalyzer()


def tokenize_to_lemmas(text):
    text = str(text).strip().replace("\n", " ").replace("\xa0", " ")
    text = text.lower()
    tokens, _ = tokenizer.tokenize(text)
    tokens = [t for t in tokens if t not in string.punctuation]
    tokens = [t for t in tokens if not t.isnumeric()]
    tokens = [t for t in tokens if len(t) >= 2]
    tokens = [morph.parse(token)[0].normal_form for token in tokens]
    return tokens


def get_tfidf_vector(text, word2idf, word2idx):
    tokens = tokenize_to_lemmas(text)
    freqs = Counter(tokens)
    tfs = {token: float(f) / len(tokens) for token, f in freqs.items()}
    data = []
    indices = []
    for token, tf in tfs.items():
        idx = word2idx.get(token, None)
        if idx is None:
            continue
        idf = word2idf.get(token, 0.0)
        tfidf = tf * idf
        data.append(tfidf)
        indices.append(idx)
    return data, indices


def load_idfs(file_name):
    word2idf = dict()
    word2idx = dict()
    with open(file_name, "r") as r:
        idx = 0
        for line in r:
            word, idf = line.strip().split("\t")
            word2idf[word] = float(idf)
            word2idx[word] = idx
            idx += 1
    return word2idf, word2idx

