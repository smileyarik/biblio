import argparse
from collections import Counter
import os
import pickle

from lightfm.lightfm import LightFM
from lightfm.data import Dataset
from tqdm import tqdm

from util import read_jsonl


def read_matrix(actions):
    datum = list()
    users = Counter()
    items = Counter()
    for a in tqdm(actions):
        user_id = a["user_id"]
        item_id = a["item_scf"]
        datum.append((user_id, item_id))
        users[user_id] += 1
        items[item_id] += 1

    removed_items = set()
    for item_id, cnt in list(items.items()):
        if cnt < 3:
            items.pop(item_id)
            removed_items.add(item_id)

    fixed_datum = list()
    for user_id, item_id in tqdm(datum):
        if item_id in removed_items:
            continue
        fixed_datum.append((user_id, item_id))

    dataset = Dataset()
    dataset.fit(list(users), list(items))
    actions_matrix = dataset.build_interactions(fixed_datum)[0]
    return dataset, actions_matrix


def main(
    input_directory,
    profile_actions_path,
    output_dataset_path,
    output_model_path,
    num_threads,
    hidden_dim,
    epochs
):
    train_actions = read_jsonl(os.path.join(input_directory, profile_actions_path))
    dataset, dataset_actions = read_matrix(train_actions)
    with open(os.path.join(input_directory, output_dataset_path), "wb") as f:
        pickle.dump(dataset, f)

    collab_model = LightFM(no_components=hidden_dim, loss="warp")
    collab_model.fit(dataset_actions, epochs=epochs, num_threads=num_threads)
    with open(os.path.join(input_directory, output_model_path), "wb") as f:
        pickle.dump(collab_model, f)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-directory", type=str, required=True)
    parser.add_argument("--profile-actions-path", type=str, required=True)
    parser.add_argument("--output-dataset-path", type=str, required=True)
    parser.add_argument("--output-model-path", type=str, required=True)
    parser.add_argument("--num-threads", type=int, default=4)
    parser.add_argument("--hidden-dim", type=int, default=32)
    parser.add_argument("--epochs", type=int, default=20)
    args = parser.parse_args()
    main(**vars(args))
