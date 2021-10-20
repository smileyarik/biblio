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
    def _get_predictions(values):
        return [x[0] for x in sorted(values, key=lambda x: x[1], reverse=True)]
    return mean([
        precision_at(_get_predictions(predictions[user_id]), user_labels, k)
        for user_id, user_labels in labels.items()
    ])


def print_metrics(predictions, labels):
    print("MAP@1:", MAP(predictions, labels, k=1))
    print("MAP@5:", MAP(predictions, labels, k=5))
    print("MAP@10:", MAP(predictions, labels, k=10))
    print("MAP@50:", MAP(predictions, labels, k=50))
    print("MAP@100:", MAP(predictions, labels, k=100))


def main(
    input_directory,
    target_actions_path,
    predictions_path
):
    true_labels = defaultdict(set)
    target_actions = read_jsonl(os.path.join(input_directory, target_actions_path))
    for action in tqdm(target_actions):
        true_labels[action["user_id"]].add(action["item_scf"])

    site_predictions = defaultdict(list)
    biblio_predictions = defaultdict(list)
    with open(os.path.join(input_directory, predictions_path)) as r:
        for line in r:
            user_id, item_id, _, prediction = line.strip().split("\t")
            if is_site_user(user_id):
                site_predictions[int(user_id)].append((int(item_id), float(prediction)))
            else:
                biblio_predictions[int(user_id)].append((int(item_id), float(prediction)))

    print("----- biblio -----")
    print_metrics(biblio_predictions, true_labels)
    print("----- site -----")
    print_metrics(site_predictions, true_labels)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--input-directory', type=str, required=True)
    parser.add_argument('--target-actions-path', type=str, required=True)
    parser.add_argument('--predictions-path', type=str, required=True)
    args = parser.parse_args()
    main(**vars(args))
