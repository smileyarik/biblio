import argparse
import os
from collections import defaultdict
from statistics import mean


def precision_at(predictions, labels, k):
    n = min(len(predictions), k)
    m = min(sum(labels), k)
    metric = 0
    tp_seen = 0
    for i in range(n):
        label = labels[i]
        if label == 1:
            tp_seen += label
            metric += tp_seen / (i + 1)
    metric /= m
    return metric


def MAP(predictions, labels, k=10):
    return mean([
        precision_at(pred, labels[user_id], k)
        for user_id, pred in predictions.items()
    ])


def main(input_directory, input_path):
    predictions = defaultdict(list)
    labels = defaultdict(list)
    with open(os.path.join(input_directory, input_path)) as r:
        for line in r:
            user_id, item_id, label, prediction = line.strip().split("\t")
            predictions[user_id].append(float(prediction))
            labels[user_id].append(int(label))
    print("MAP@1:", MAP(predictions, labels, k=1))
    print("MAP@5:", MAP(predictions, labels, k=5))
    print("MAP@10:", MAP(predictions, labels, k=10))
    print("MAP@50:", MAP(predictions, labels, k=50))
    print("MAP@100:", MAP(predictions, labels, k=100))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--input-directory', type=str, required=True)
    parser.add_argument('--input-path', type=str, required=True)
    args = parser.parse_args()
    main(**vars(args))
