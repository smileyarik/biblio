import argparse
from collections import defaultdict
import json
import os
import random

from tqdm import tqdm

from util import read_jsonl, write_jsonl


def main(
    input_directory,
    profile_actions_path,
    target_actions_path,
    start_ts,
    output_path,
    top_k
):

    print("Read target users")
    target_user_ids = set()
    target_action_gen = read_jsonl(os.path.join(input_directory, target_actions_path))
    for action in tqdm(target_action_gen):
        target_user_ids.add(action["user_id"])

    print("Parsing transactions")
    user_links = defaultdict(set)
    item_links = defaultdict(set)
    profile_action_gen = read_jsonl(os.path.join(input_directory, profile_actions_path))
    for action in tqdm(profile_action_gen):
        user_id = action["user_id"]
        item_id = action["item_scf"]
        ts = action["ts"]
        if ts >= start_ts:
            user_links[user_id].add(item_id)
            item_links[item_id].add(user_id)

    print("Calulating random walk...")
    graph = defaultdict(lambda: defaultdict(float))
    for user1 in tqdm(list(target_user_ids)):
        user2user = defaultdict(float)
        user1_items = user_links[user1]
        for item_id in user1_items:
            w = 1.0 / len(user1_items)
            item_users = item_links[item_id]
            for user2 in item_users:
                user2user[user2] += w / len(item_users)

        user1_new_items = defaultdict(float)
        for user2, w in user2user.items():
            user2_items = user_links[user2]
            for item_id in user2_items:
                if item_id in user1_items:
                    continue
                user1_new_items[item_id] += w / len(user2_items)

        user1_new_items = sorted(user1_new_items.items(), key=lambda x: x[1], reverse=True)
        for i, (item_id, weight) in enumerate(user1_new_items):
            if i >= top_k:
                break
            graph[user_id][item_id] = weight

    print("Dumping graph")
    with open(os.path.join(input_directory, output_path), "w") as fw:
        for user, items in graph.items():
            for item, weight in items.items():
                r = {"user": user, "item": item, "weight": weight}
                fw.write(json.dumps(r, ensure_ascii=False).strip() + "\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-directory", type=str, required=True)
    parser.add_argument("--profile-actions-path", type=str, required=True)
    parser.add_argument("--target-actions-path", type=str, required=True)
    parser.add_argument("--output-path", type=str, required=True)
    parser.add_argument("--start-ts", type=int, required=True)
    parser.add_argument("--top-k", type=int, default=1000)
    args = parser.parse_args()
    main(**vars(args))
