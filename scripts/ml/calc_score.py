import argparse
import os
from collections import defaultdict
from statistics import mean
from tqdm import tqdm
from util import is_site_user, read_jsonl


def precision_at(predictions, true_labels, k):
    assert len(true_labels) > 0 # really need?
    assert len(set(predictions)) == len(predictions) # dups protection
    tp_seen = 0
    metric = 0
    for i, item_id in enumerate(predictions[:k]):
        if item_id in true_labels:
            tp_seen += 1
            metric += tp_seen / (i + 1)
    metric /= min(len(true_labels), k)
    return metric


def MAP(predictions, labels, k=10):
    return mean([
        precision_at(user_predictions, user_labels, k)
        for user_predictions, user_labels in zip(predictions, labels)
    ])


def print_metrics(predictions, labels):
    print("MAP@1  : {:.20f}".format(MAP(predictions, labels, k=1)))
    print("MAP@5  : {:.20f}".format(MAP(predictions, labels, k=5)))
    print("MAP@10 : {:.20f}".format(MAP(predictions, labels, k=10)))
    print("MAP@50 : {:.20f}".format(MAP(predictions, labels, k=50)))
    print("MAP@100: {:.20f}".format(MAP(predictions, labels, k=100)))


def main(
    input_directory,
    target_actions_path,
    predictions_path
):
    print("Reading data")
    predictions = defaultdict(list)
    with open(os.path.join(input_directory, predictions_path)) as r:
        for line in tqdm(r):
            user_id, item_id, _, prediction = line.strip().split("\t")
            predictions[int(user_id)].append((int(item_id), float(prediction)))

    labels = defaultdict(set)
    target_actions = read_jsonl(os.path.join(input_directory, target_actions_path))
    for action in tqdm(target_actions):
        labels[action["user_id"]].add(action["item_scf"])

    # predictions ⊂ labels, missing user_ids ~ zero precision
    assert predictions.keys() <= labels.keys()

    print("Calculating metrics")
    site_predictions = []
    site_labels = []
    biblio_predictions = []
    biblio_labels = []

    for user_id, user_labels in labels.items():
        user_predictions = [x[0] for x in sorted(predictions[user_id], key=lambda x: x[1], reverse=True)]
        if is_site_user(user_id):
            site_predictions.append(user_predictions)
            site_labels.append(user_labels)
        else:
            biblio_predictions.append(user_predictions)
            biblio_labels.append(user_labels)

    print("----- site -----")
    print(len(site_labels))
    print_metrics(site_predictions, site_labels)
    print("----- biblio -----")
    print(len(biblio_labels))
    print_metrics(biblio_predictions, biblio_labels)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--input-directory', type=str, required=True)
    parser.add_argument('--target-actions-path', type=str, required=True)
    parser.add_argument('--predictions-path', type=str, required=True)
    args = parser.parse_args()
    main(**vars(args))
