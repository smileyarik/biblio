import argparse
import os
import pickle

from lightfm.lightfm import LightFM
from lightfm.data import Dataset
from tqdm import tqdm

from util import read_jsonl


def read_matrix(actions):
    datum = list()
    users = set()
    items = set()
    for a in tqdm(actions):
        user_id = a["user_id"]
        item_id = a["item_scf"]
        datum.append((user_id, item_id))
        users.add(user_id)
        items.add(item_id)
    dataset = Dataset()
    dataset.fit(list(users), list(items))
    actions_matrix = dataset.build_interactions(datum)[0]
    return dataset, actions_matrix


def main(
    input_directory,
    train_actions_path,
    output_dataset_path,
    output_model_path
):
    train_actions = read_jsonl(os.path.join(input_directory, train_actions_path))
    dataset, dataset_actions = read_matrix(train_actions)
    with open(os.path.join(input_directory, output_dataset_path), "wb") as f:
        pickle.dump(dataset, f)

    collab_model = LightFM(no_components=64, loss="warp")
    collab_model.fit(dataset_actions, epochs=30, num_threads=3)
    with open(os.path.join(input_directory, output_model_path), "wb") as f:
        pickle.dump(collab_model, f)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-directory", type=str, required=True)
    parser.add_argument("--train-actions-path", type=str, required=True)
    parser.add_argument("--output-dataset-path", type=str, required=True)
    parser.add_argument("--output-model-path", type=str, required=True)
    args = parser.parse_args()
    main(**vars(args))
