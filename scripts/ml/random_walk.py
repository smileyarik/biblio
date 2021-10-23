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
    probability
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
        item_id = action["item_scf"]
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
            if random.random() > probability:
                continue
            w = 1.0 / len(user1_items)
            item_users = item_links[item_id]
            for user2 in item_users:
                if random.random() > probability:
                    continue
                user2user[user2] += w / len(item_users)

        for user2, w in user2user.items():
            user2_items = user_links[user2]
            for item_id in user2_items:
                if random.random() > probability:
                    continue
                graph[user1][item_id] += w / len(user2_items)

    print("Dumping graph")
    with open(os.path.join(input_directory, output_path), "w") as w:
        for user, items in graph.items():
            toptop = sorted([(item,weight) for item,weight in items.items()], key=lambda x:-x[1])[0:500]
            for item, weight in toptop:
                r = {"user": user, "item": item, "weight": weight}
                w.write(json.dumps(r, ensure_ascii=False).strip() + "\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-directory", type=str, required=True)
    parser.add_argument("--profile-actions-path", type=str, required=True)
    parser.add_argument("--target-actions-path", type=str, required=True)
    parser.add_argument("--output-path", type=str, required=True)
    parser.add_argument("--start-ts", type=int, required=True)
    parser.add_argument("--probability", type=float, default=1.0)
    args = parser.parse_args()
    main(**vars(args))
