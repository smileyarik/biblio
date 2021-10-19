import argparse
import json
import os

from collections import defaultdict
from tqdm import tqdm

from util import read_jsonl, is_site_user


SITE_USER_VALID_ACTION_COUNT = 5


def write_record(f, record):
    f.write(json.dumps(record, ensure_ascii=False).strip() + "\n")


def main(
    start_train_ts,
    finish_train_ts,
    start_valid_ts,
    finish_valid_ts,
    input_directory,
    actions_path,
    train_stat_path,
    train_target_path,
    valid_stat_path,
    valid_target_path,
    test_stat_path
):
    actions = read_jsonl(os.path.join(input_directory, actions_path))
    train_stat = open(os.path.join(input_directory, train_stat_path), "w")
    train_target = open(os.path.join(input_directory, train_target_path), "w")
    valid_stat = open(os.path.join(input_directory, valid_stat_path), "w")
    valid_target = open(os.path.join(input_directory, valid_target_path), "w")
    test_stat = open(os.path.join(input_directory, test_stat_path), "w")

    site_user_actions = defaultdict(list)

    for action in tqdm(actions):
        ts = action["ts"]
        user_id = action["user_id"]
        if action["has_bad_item"] or action["has_bad_user"]:
            continue
        if is_site_user(user_id):
            site_user_actions[user_id].append(action)
            continue
        write_record(test_stat, action)
        if ts < start_train_ts:
            write_record(train_stat, action)
            write_record(valid_stat, action)
        elif ts < finish_train_ts:
            write_record(train_target, action)
            write_record(valid_stat, action)
        elif ts < start_valid_ts:
            write_record(valid_stat, action)
        elif ts < finish_valid_ts:
            write_record(valid_target, action)

    for _, actions in site_user_actions.items():
        actions.sort(key=lambda a: a["ts"])
        for action in actions[:-SITE_USER_VALID_ACTION_COUNT]:
            write_record(valid_stat, action)
        for action in actions[-SITE_USER_VALID_ACTION_COUNT:]:
            write_record(valid_target, action)

    train_stat.close()
    train_target.close()
    valid_stat.close()
    valid_target.close()
    test_stat.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--input-directory', type=str, required=True)
    parser.add_argument('--actions-path', type=str, required=True)
    parser.add_argument('--start-train-ts', type=int, required=True)
    parser.add_argument('--finish-train-ts', type=int, required=True)
    parser.add_argument('--train-stat-path', type=str, required=True)
    parser.add_argument('--train-target-path', type=str, required=True)
    parser.add_argument('--start-valid-ts', type=int, required=True)
    parser.add_argument('--finish-valid-ts', type=int, required=True)
    parser.add_argument('--valid-stat-path', type=str, required=True)
    parser.add_argument('--valid-target-path', type=str, required=True)
    parser.add_argument('--test-stat-path', type=str, required=True)
    args = parser.parse_args()
    main(**vars(args))
