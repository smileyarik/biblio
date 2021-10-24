import argparse
import os
import random
from sklearn.feature_extraction.text import TfidfVectorizer

from tqdm import tqdm

from prepare.tfidf import tokenize_to_lemmas
from util import read_jsonl


def build_idf_vocabulary(texts, max_df=0.05, min_df=3):
    print("Building TfidfVectorizer...")
    vectorizer = TfidfVectorizer(tokenizer=tokenize_to_lemmas, max_df=max_df, min_df=min_df)
    vectorizer.fit(texts)
    idf_vector = vectorizer.idf_.tolist()

    print("{} words in vocabulary".format(len(idf_vector)))
    idfs = list()
    for word, idx in vectorizer.vocabulary_.items():
        idfs.append((word, idf_vector[idx]))

    idfs.sort(key=lambda x: (x[1], x[0]))
    return idfs


def main(
    input_directory,
    all_books_path,
    output_file,
    nrows
):
    print("Parsing input data...")
    texts = []
    for item in tqdm(read_jsonl(os.path.join(input_directory, all_books_path))):
        if annotation := item.get("annotation", None):
            annotation = " ".join(annotation.split()[:200])
            texts.append(annotation)
        if title := item.get("title", None):
            texts.append(title)

    random.shuffle(texts)
    texts = texts if nrows is None else texts[:nrows]
    idfs = build_idf_vocabulary(texts)
    print("Saving vocabulary with IDFs...")
    with open(output_file, "w") as w:
        for word, idf in idfs:
            w.write("{}\t{}\n".format(word, idf))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--input-directory', type=str, required=True)
    parser.add_argument('--all-books-path', type=str, default="all_books.jsonl")
    parser.add_argument('--output-file', type=str, required=True)
    parser.add_argument('--nrows', type=int, default=None)
    args = parser.parse_args()
    main(**vars(args))
