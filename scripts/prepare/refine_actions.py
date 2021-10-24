import argparse
import json
import os

from tqdm import tqdm

from util import read_csv_files, read_csv, date_to_ts, datetime_to_ts, read_jsonl, write_jsonl
from util import BIBLIO_USERS_ID_OFFSET, BIBLIO_ACTIONS_ID_OFFSET


def main(
    input_directory,
    actions_pattern,
    bookpoints_path,
    new_actions_path,
    output_path,
    refined_items_path,
    refined_users_path
):
    bookpoint_to_lib = {}
    print("Read bookpoint data")
    # id;cbs;name;adress;eisk
    for row in tqdm(read_csv(os.path.join(input_directory, bookpoints_path), encoding="cp1251")):
        if row["eisk"] != '' and row["id"] != '':
            bookpoint_to_lib[int(row["id"])] = int(row["eisk"])

    print("Reading items...")
    assert os.path.exists(refined_items_path)
    items = [{
        "id": i["id"],
        "scf_id": i["scf_id"]
    } for i in read_jsonl(refined_items_path)]
    items = {item["id"]: item for item in items}
    print("... {} items read".format(len(items)))

    print("Reading users...")
    assert os.path.exists(refined_users_path)
    users = list(read_jsonl(refined_users_path))
    users = {user["id"]: user for user in users}
    print("... {} users read".format(len(users)))

    print("Processing biblio/actions...")
    actions_gen = read_csv_files(
        directory=input_directory,
        pattern=actions_pattern,
        encoding="cp1251"
    )

    bad_actions_by_item_count = 0
    bad_actions_by_user_count = 0
    actions = []
    for a in tqdm(actions_gen):
        user_id = int(a["readerID"]) + BIBLIO_USERS_ID_OFFSET
        action = {
            "id": int(a["circulationID"]) + BIBLIO_ACTIONS_ID_OFFSET,
            "item_id": int(a["catalogueRecordID"]),
            "user_id": user_id,
            "ts": date_to_ts(a["startDate"]),
            "duration": date_to_ts(a["finishDate"]) - date_to_ts(a["startDate"]),
            "type": "take",
            "has_bad_item": False,
            "has_bad_user": False,
            "item_scf": None,
            "library": None
        }
        if int(a["bookpointID"]) in bookpoint_to_lib:
            action["library"] = bookpoint_to_lib[int(a["bookpointID"])]
        user = users[user_id]
        if user["actions_count"] >= 500:
            bad_actions_by_user_count += 1
            action["has_bad_user"] = True

        if item := items.get(action["item_id"], None):
            action["item_scf"] = item["scf_id"]
        else:
            bad_actions_by_item_count += 1
            action["has_bad_item"] = True
        actions.append(action)
    print("... {} actions processed".format(len(actions)))

    print("Processing new actions...")
    for i, a in enumerate(tqdm(read_csv(os.path.join(input_directory, new_actions_path)))):
        action = {
            "id": i,
            "user_id": int(a["user_id"]),
            "item_id": int(a["source_url"].split("/")[-2]),
            "ts": datetime_to_ts(a["dt"]),
            "duration": -1,
            "type": a["event"],
            "has_bad_item": False,
            "has_bad_user": False,
            "item_scf": None,
            "library": None
        }
        if item := items.get(action["item_id"], None):
            action["item_scf"] = item["scf_id"]
        else:
            bad_actions_by_item_count += 1
            action["has_bad_item"] = True
        actions.append(action)

    actions.sort(key=lambda x: x["ts"])

    print("... {} actions overall".format(len(actions)))
    print("... {} bad actions by item".format(bad_actions_by_item_count))
    print("... {} bad actions by user".format(bad_actions_by_user_count))
    write_jsonl(output_path, actions)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--output-path', type=str, required=True)
    parser.add_argument('--input-directory', type=str, required=True)
    parser.add_argument('--actions-pattern', type=str, default="circulaton_*.csv")
    parser.add_argument('--bookpoints-path', type=str, default="bookpoints.csv")
    parser.add_argument('--new-actions-path', type=str, default="actions.csv")
    parser.add_argument('--refined-items-path', type=str, required=True)
    parser.add_argument('--refined-users-path', type=str, required=True)
    args = parser.parse_args()
    main(**vars(args))
