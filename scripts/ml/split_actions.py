import argparse
import datetime
import json
import os

from tqdm import tqdm


def main(
    actions_path,
    start_train_ts,
    end_train_ts,
    start_valid_ts,
    end_valid_ts,
    output_directory,
    train_profile_actions_path,
    train_target_actions_path,
    valid_profile_actions_path,
    valid_target_actions_path
):
    def _parse_ts(value):
        return datetime.datetime.fromisoformat(value).timestamp()
    start_train_ts = _parse_ts(start_train_ts)
    end_train_ts = _parse_ts(end_train_ts)
    start_valid_ts = _parse_ts(start_valid_ts)
    end_valid_ts = _parse_ts(end_valid_ts)

    train_profile_actions_f = open(os.path.join(output_directory, train_profile_actions_path), 'w')
    train_target_actions_f = open(os.path.join(output_directory, train_target_actions_path), 'w')
    valid_profile_actions_f = open(os.path.join(output_directory, valid_profile_actions_path), 'w')
    valid_target_actions_f = open(os.path.join(output_directory, valid_target_actions_path), 'w')

    with open(actions_path, 'r') as actions_f:
        for row in tqdm(actions_f):
            ts = json.loads(row.rstrip())['ts']
            if ts < start_train_ts:
                train_profile_actions_f.write(row)
                valid_profile_actions_f.write(row)
            elif ts < end_train_ts:
                train_target_actions_f.write(row)
                valid_profile_actions_f.write(row)
            elif ts < start_valid_ts:
                valid_profile_actions_f.write(row)
            elif ts < end_valid_ts:
                valid_target_actions_f.write(row)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--actions-path', type=str, required=True)
    parser.add_argument('--start-train-ts', type=str, required=True, help='1970-01-01')
    parser.add_argument('--end-train-ts', type=str, required=True)
    parser.add_argument('--start-valid-ts', type=str, required=True)
    parser.add_argument('--end-valid-ts', type=str, required=True)
    parser.add_argument('--output-directory', type=str, required=True)
    parser.add_argument('--train-profile-actions-path', type=str, default="train_profile_actions.jsonl")
    parser.add_argument('--train-target-actions-path', type=str, default="train_target_actions.jsonl")
    parser.add_argument('--valid-profile-actions-path', type=str, default="valid_profile_actions.jsonl")
    parser.add_argument('--valid-target-actions-path', type=str, default="valid_target_actions.jsonl")
    args = parser.parse_args()
    main(**vars(args))
