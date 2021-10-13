import argparse
from collections import Counter
import os

from tqdm import tqdm

from util import read_csv, write_jsonl, BIBLIO_USERS_ID_OFFSET, read_csv_files

def main(
    input_directory,
    actions_pattern,
    output_path,
    readers_file,
    new_actions_file
):
    print("Reading biblio/actions...")
    actions_gen = read_csv_files(
        directory=input_directory,
        pattern=actions_pattern,
        encoding="cp1251"
    )
    users = dict()
    users_counter = Counter()
    for a in tqdm(actions_gen):
        user_id = int(a["readerID"]) + BIBLIO_USERS_ID_OFFSET
        users_counter[user_id] += 1
        users[user_id] = {
            "id": user_id,
            "type": "biblio",
            "actions_count": 0
        }

    print("Reading biblio/readers...")
    users_gen = read_csv(
        os.path.join(input_directory, readers_file),
        encoding="cp1251",
        header=("id", "birth_date", "address")
    )
    for u in users_gen:
        user_id = int(u["id"]) + BIBLIO_USERS_ID_OFFSET
        user = {
            "id": user_id,
            "type": "biblio",
            "actions_count": 0,
            "meta": {
                "birth_date": u["birth_date"],
                "address": u["address"],
            }
        }
        users[user_id] = user

    print("Processing site/actions...")
    for a in read_csv(os.path.join(input_directory, new_actions_file)):
        user_id = int(a["user_id"])
        user = {
            "id": user_id,
            "type": "site",
            "actions_count": 0,
            "meta": {}
        }
        users[user_id] = user
        users_counter[user_id] += 1

    print("Writing user actions count...")
    for user_id, cnt in users_counter.most_common():
        users[user_id]["actions_count"] = cnt

    print("Writing output...")
    users = list(users.values())
    users.sort(key=lambda x: x["id"])
    write_jsonl(output_path, users)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--output-path', type=str, required=True)
    parser.add_argument('--input-directory', type=str, required=True)
    parser.add_argument('--readers-file', type=str, default="readers.csv")
    parser.add_argument('--actions-pattern', type=str, default="circulaton_*.csv")
    parser.add_argument('--new-actions-file', type=str, default="actions.csv")
    args = parser.parse_args()
    main(**vars(args))
