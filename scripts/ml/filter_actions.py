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
    new_actions_path,
    site
):
    new_actions = open(os.path.join(input_directory, new_actions_path), "w")

    actions = read_jsonl(os.path.join(input_directory, actions_path))
    for action in tqdm(actions):
        if action["has_bad_item"] or action["has_bad_user"]:
            continue
        if site and not is_site_user(action["user_id"]):
            continue
        write_record(new_actions, action)

    new_actions.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--input-directory', type=str, required=True)
    parser.add_argument('--actions-path', type=str, required=True)
    parser.add_argument('--new-actions-path', type=str, required=True)
    parser.add_argument('--site', action="store_true", default=False)
    args = parser.parse_args()
    main(**vars(args))
