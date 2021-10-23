import argparse
import itertools
import pickle
import random
import os
from collections import defaultdict

from tqdm import tqdm

from ml.profiles import OT, CT, RT, Counters, Profile
from ml.features_lib import ColumnDescription, counter_cos, FeaturesCalcer
from util import read_jsonl


PREDICTION_LIMIT = 100
RANDOM_SEED = 23


def calc_popular_baseline(
    target_users,
    items,
    filter_items,
):
    top = []
    for item_id, item in items.items():
        item_size = float(item.counters.get(OT.GLOBAL, CT.BOOKING, RT.D30, '', 1633028400)) # 1 октября 2021 г., fix it
        top.append((item_id, item_size))
    top = sorted(top, key=lambda x: x[1], reverse=True)

    predictions = []
    for user_id in tqdm(target_users):
        filtered_top = filter(lambda x: x[0] not in filter_items[user_id], top)
        for item_id, score in itertools.islice(filtered_top, PREDICTION_LIMIT):
            predictions.append((user_id, item_id, score))
    return predictions


def calc_rw_baseline(
    target_users,
    rw_path,
    filter_items,
):
    rw_graph = defaultdict(list)
    for record in read_jsonl(rw_path):
        rw_graph[record["user"]].append((record["item"], record["weight"]))

    predictions = []
    for user_id in tqdm(target_users):
        top = sorted(rw_graph[user_id], key=lambda x: x[1], reverse=True)
        filtered_top = filter(lambda x: x[0] not in filter_items[user_id], top)
        for item_id, score in itertools.islice(filtered_top, PREDICTION_LIMIT):
            predictions.append((user_id, item_id, score))
    return predictions


def calc_random_baseline(
    target_users,
    items,
    filter_items,
):
    random.seed(RANDOM_SEED)

    predictions = []
    for user_id in tqdm(target_users):
        top = random.sample(items.keys(), k=PREDICTION_LIMIT+len(filter_items[user_id]))
        filtered_top = filter(lambda x: x not in filter_items[user_id], top)
        for i, item_id in enumerate(itertools.islice(filtered_top, PREDICTION_LIMIT)):
            predictions.append((user_id, item_id, PREDICTION_LIMIT - i))
    return predictions


def main(
    baseline_name,
    input_directory,
    item_profiles_path,
    user_profiles_path,
    profile_actions_path,
    target_actions_path,
    rw_path,
    output_path,
):
    print("Read item profiles")
    items = dict()
    with open(os.path.join(input_directory, item_profiles_path), "r") as r:
        for line in tqdm(r):
            profile = Profile.loads(line)
            items[profile.object_id] = profile
    print("...{} items read".format(len(items)))

    print("Read target users")
    target_users = set()
    target_items = defaultdict(set)
    target_actions = read_jsonl(os.path.join(input_directory, target_actions_path))
    for action in tqdm(target_actions):
        target_users.add(action["user_id"])
        target_items[action["user_id"]].add(action["item_scf"])
    print("...{} target users".format(len(target_users)))

    print("Read already seen items")
    filter_items = defaultdict(set)
    stat_actions = read_jsonl(os.path.join(input_directory, profile_actions_path))
    for action in tqdm(stat_actions):
        filter_items[action["user_id"]].add(action["item_scf"])

    print(f"Calculating baseline \"{baseline_name}\"")
    if baseline_name == "popular":
        predictions = calc_popular_baseline(target_users, items, filter_items)
    elif baseline_name == "random_walk":
        rw_path = os.path.join(input_directory, rw_path)
        predictions = calc_rw_baseline(target_users, rw_path, filter_items)
    elif baseline_name == "random":
        predictions = calc_random_baseline(target_users, items, filter_items)
    else:
        raise "unknown baseline name"

    with open(os.path.join(input_directory, output_path), "w") as w:
        for user_id, item_id, score in predictions:
            y_true = int(item_id in target_items[user_id])
            w.write("{}\t{}\t{}\t{}\n".format(user_id, item_id, y_true, score))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--input-directory', type=str, required=True)
    parser.add_argument('--item-profiles-path', type=str, required=True)
    parser.add_argument('--user-profiles-path', type=str, required=True)
    parser.add_argument('--profile-actions-path', type=str, required=True)
    parser.add_argument('--target-actions-path', type=str, required=True)
    parser.add_argument('--rw-path', type=str, required=True)
    parser.add_argument('--baseline-name', type=str, required=True)
    parser.add_argument('--output-path', type=str, required=True)
    args = parser.parse_args()
    main(**vars(args))
