import argparse
import os
import pickle

from lightfm import LightFM
from lightfm.data import Dataset
from scipy.sparse import save_npz
from sklearn.base import clone
from tqdm import tqdm
import numpy as np

from ml.collab import LightFMResizable
from util import read_jsonl


def predict_collab(user_id, k, model, dataset):
    user_mapping, _, item_mapping, _ = dataset.mapping()
    reverse_item_mapping = {v: k for k, v in item_mapping.items()}
    if user_idx := user_mapping.get(user_id):
        items_indices = np.arange(dataset.interactions_shape()[1])
        scores = model.predict(user_idx, items_indices)
        return [reverse_item_mapping.get(i) for i in np.argsort(-scores)[:k]]
    return []


def main(
    input_directory,
    dataset_path,
    model_path,
    test_actions_path,
    output_path
):
    with open(os.path.join(input_directory, dataset_path), "rb") as r:
        dataset = pickle.load(r)

    with open(os.path.join(input_directory, model_path), "rb") as r:
        model = pickle.load(r)

    test_actions = read_jsonl(os.path.join(input_directory, test_actions_path))
    test_users = list(sorted({a["user_id"] for a in test_actions}))

    with open(os.path.join(input_directory, output_path), "w") as w:
        for user_id in tqdm(test_users):
            items = predict_collab(user_id, 100, model, dataset)
            for i, item_id in enumerate(items):
                w.write("{}\t{}\t{}\t{}\n".format(user_id, item_id, 0, (1.0 - i / len(items))))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-directory", type=str, required=True)
    parser.add_argument("--dataset-path", type=str, required=True)
    parser.add_argument("--model-path", type=str, required=True)
    parser.add_argument("--test-actions-path", type=str, required=True)
    parser.add_argument("--output-path", type=str, required=True)
    args = parser.parse_args()
    main(**vars(args))
