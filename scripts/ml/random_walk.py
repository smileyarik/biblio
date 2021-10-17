import argparse
import os
from collections import defaultdict

from tqdm import tqdm

from util import read_jsonl, write_jsonl


def main(
    input_directory,
    profile_actions_path,
    target_actions_path,
    start_ts,
    output_path
):

    print("Read target users")
    target_user_ids = set()
    target_action_gen = read_jsonl(os.path.join(input_directory, target_actions_path))
    for action in tqdm(target_action_gen):
        target_user_ids.add(action["user_id"])

    print("Parsing transactions")
    user_links = defaultdict(list)
    item_links = defaultdict(list)
    profile_action_gen = read_jsonl(os.path.join(input_directory, profile_actions_path))
    for action in tqdm(profile_action_gen):
        user_id = action["user_id"]
        item_id = action["item_uniq_id"]
        ts = action["ts"]
        if ts >= start_ts:
            user_links[user_id].append(item_id)
            item_links[item_id].append(user_id)

    print("Calulating random walk...")
    graph = defaultdict(lambda: defaultdict(float))
    for user1 in tqdm(target_user_ids):
        user2user = defaultdict(float)
        user1_items = user_links[user1]
        for item_id in user1_items:
            w = 1.0 / len(user1_items)
            item_users = item_links[item_id]
            for user2 in item_users:
                user2user[user2] += w / len(item_users)

        for user2, w in user2user.items():
            user2_items = user_links[user2]
            for item_id in user2_items:
                graph[user1][item_id] += w / len(user2_items)

    print("Dumping graph")
    records = []
    for user, items in graph.items():
        for item, weight in items.items():
            records.append({"user": user, "item": item, "weight": weight})
    write_jsonl(os.path.join(input_directory, output_path), records)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-directory", type=str, required=True)
    parser.add_argument("--profile-actions-path", type=str, required=True)
    parser.add_argument("--target-actions-path", type=str, required=True)
    parser.add_argument("--output-path", type=str, required=True)
    parser.add_argument("--start-ts", type=int, required=True)
    args = parser.parse_args()
    main(**vars(args))
