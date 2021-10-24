import argparse
import json
import os

from tqdm import tqdm
from util import read_jsonl, is_site_user


def write_record(f, record):
    f.write(json.dumps(record, ensure_ascii=False).strip() + "\n")


def main(
    input_directory,
    actions_path,
    site_actions_path
):
    site_actions = open(os.path.join(input_directory, site_actions_path), "w")

    actions = read_jsonl(os.path.join(input_directory, actions_path))
    for action in tqdm(actions):
        if action["has_bad_item"]: # action with unknown item
            continue
        if not is_site_user(action["user_id"]):
            continue
        write_record(site_actions, action)

    site_actions.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--input-directory', type=str, required=True)
    parser.add_argument('--actions-path', type=str, required=True)
    parser.add_argument('--site-actions-path', type=str, required=True)
    args = parser.parse_args()
    main(**vars(args))
