import argparse
from sklearn.feature_extraction.text import TfidfVectorizer

from tqdm import tqdm

from ml.tfidf import tokenize_to_lemmas
from util import read_jsonl


def build_idf_vocabulary(texts, max_df=0.2, min_df=20):
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
    refined_items_path,
    output_file
):
    print("Parsing input data...")
    texts = []
    for item in tqdm(read_jsonl(refined_items_path)):
        if annotation := item["meta"].get("annotation", None):
            texts.append(annotation)

    idfs = build_idf_vocabulary(texts)
    print("Saving vocabulary with IDFs...")
    with open(output_file, "w") as w:
        for word, idf in idfs:
            w.write("{}\t{}\n".format(word, idf))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--refined-items-path', type=str, required=True)
    parser.add_argument('--output-file', type=str, required=True)
    args = parser.parse_args()
    main(**vars(args))
