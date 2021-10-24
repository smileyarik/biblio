import argparse
import pickle
import os
from collections import defaultdict

from tqdm import tqdm

from ml.profiles import OT, CT, RT, Counters, Profile
from ml.features_lib import ColumnDescription, counter_cos, FeaturesCalcer
from util import read_jsonl, is_site_user


def main(
    input_directory,
    item_profiles_path,
    user_profiles_path,
    target_actions_path,
    rw_top_size,
    lstm_top_size,
    items_per_group,
    start_ts,
    profile_actions_path,
    rw_path,
    lstm_path
):
    poptop = items_per_group - rw_top_size - lstm_top_size
    print(poptop, rw_top_size, lstm_top_size)
    assert poptop >= 0

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

    print("Random walk load")
    rw_records = read_jsonl(os.path.join(input_directory, rw_path))
    rw_graph = defaultdict(lambda: defaultdict(float))
    for record in tqdm(rw_records):
        rw_graph[record["user"]][record["item"]] = record["weight"]

    print("LSTM load")
    lstm_records = read_jsonl(os.path.join(input_directory, lstm_path))
    lstm_graph = defaultdict(lambda: defaultdict(float))
    for record in tqdm(lstm_records):
        lstm_graph[record["user"]][record["item"]] = record["weight"]

    print("Calc candidates")
    book_top = []
    for item_id, item in items.items():
        item_size = float(item.counters.get(OT.GLOBAL, CT.BOOKING, RT.D7, '', start_ts))
        book_top.append((item_id, item_size))
    book_top = sorted(book_top, key=lambda x:-x[1])

    aaa = 0
    bad_candidates_count = 0
    all_targets_found = 0
    for user_id in tqdm(target_users):
        targets_found = [0, 0, 0]
        count = 0
        aaa += 1
        user_items = set()
        for item_id, _ in book_top[:poptop]:
            if item_id in filter_items[user_id] or item_id in user_items:
                continue
            count += 1
            user_items.add(item_id)
            if item_id in target_items[user_id]:
                targets_found[0] += 1

        last_count = count
        for item_id, value in rw_graph.get(user_id, {}).items():
            if item_id in filter_items[user_id] or item_id in user_items:
                continue
            if count == last_count + rw_top_size:
                break
            count += 1
            user_items.add(item_id)
            if item_id in target_items[user_id]:
                targets_found[1] += 1

        last_count = count
        for item_id, value in lstm_graph.get(user_id, {}).items():
            if item_id in filter_items[user_id] or item_id in user_items:
                continue
            if count == last_count + lstm_top_size:
                break
            count += 1
            user_items.add(item_id)
            if item_id in target_items[user_id]:
                targets_found[2] += 1

        tail_top = book_top[poptop:]
        for item_id, _ in tail_top:
            if count == items_per_group:
                break
            if item_id in filter_items[user_id] or item_id in user_items:
                continue
            count += 1
            user_items.add(item_id)
            if item_id in target_items[user_id]:
                targets_found[0] += 1

        all_targets_found += sum(targets_found)
        if aaa % 1000 == 1:
            print(all_targets_found)

        if sum(targets_found) == 0:
            bad_candidates_count += 1

    print("Users with bad candidates: {}".format(bad_candidates_count))
    print("Targets found:", all_targets_found)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--input-directory', type=str, required=True)
    parser.add_argument('--item-profiles-path', type=str, required=True)
    parser.add_argument('--user-profiles-path', type=str, required=True)
    parser.add_argument('--profile-actions-path', type=str, required=True)
    parser.add_argument('--target-actions-path', type=str, required=True)
    parser.add_argument('--rw-top-size', type=int, default=200)
    parser.add_argument('--lstm-top-size', type=int, default=200)
    parser.add_argument('--items-per-group', type=int, default=600)
    parser.add_argument('--start-ts', type=int, required=True)
    parser.add_argument('--rw-path', type=str, required=True)
    parser.add_argument('--lstm-path', type=str, required=True)
    args = parser.parse_args()
    main(**vars(args))
