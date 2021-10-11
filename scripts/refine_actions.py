import argparse
import json
import os

from tqdm import tqdm

from util import read_csv_files, read_csv, date_to_ts, datetime_to_ts, read_jsonl


def main(
    actions_directory,
    actions_prefix,
    new_actions_path,
    output_path,
    refined_books_path,
    refined_users_path
):

    print("Reading items...")
    assert os.path.exists(refined_books_path)
    items = read_jsonl(refined_books_path)
    items = {item["id"]: item for item in items}
    print("{} items read".format(len(items)))

    print("Reading users...")
    assert os.path.exists(refined_users_path)
    users = list(read_jsonl(refined_users_path))
    new_user_offset = min([u["id"] for u in users if u["type"] == "site"]) - 1
    users = {user["id"]: user for user in users}
    print("{} users read".format(len(users)))

    print("Processing main actions...")
    actions_gen = read_csv_files(
        directory=actions_directory,
        prefix=actions_prefix,
        encoding="cp1251"
    )

    actions_count = 0
    bad_actions_by_item_count = 0
    bad_actions_by_user_count = 0
    max_action_id = 0
    with open(output_path, "w") as w:
        for a in tqdm(actions_gen):
            action = {
                "id": int(a["circulationID"]),
                "item_id": int(a["catalogueRecordID"]),
                "user_id": int(a["readerID"]),
                "ts": date_to_ts(a["startDate"]),
                "type": "take",
                "has_bad_item": False,
                "has_bad_user": False
            }
            if action["item_id"] not in items:
                bad_actions_by_item_count += 1
                action["has_bad_item"] = True
            item = items.get(action["item_id"], {})

            if not action["has_bad_item"] and action["user_id"] not in users:
                bad_actions_by_user_count += 1
                action["has_bad_user"] = True
            user = users.get(action["user_id"], {})
            if not action["has_bad_item"] and user and user["type"] != "biblio":
                bad_actions_by_user_count += 1
                action["has_bad_user"] = True

            action["item_uniq_id"] = item.get("uniq_id", None)
            max_action_id = max(max_action_id, action["id"])
            actions_count += 1
            w.write(json.dumps(action, ensure_ascii=False).strip() + "\n")
        print("{} actions processed".format(actions_count))

        print("Processing new actions...")
        for i, a in enumerate(tqdm(read_csv(new_actions_path))):
            action = {
                "id": max_action_id + i + 1,
                "user_id": int(a["user_id"]) + new_user_offset,
                "item_id": int(a["source_url"].split("/")[-2]),
                "ts": datetime_to_ts(a["dt"]),
                "type": a["event"],
                "has_bad_item": False,
                "has_bad_user": False
            }
            assert action["item_id"] in items
            item = items[action["item_id"]]
            action["item_uniq_id"] = item["uniq_id"]
            actions_count += 1
            w.write(json.dumps(action, ensure_ascii=False).strip() + "\n")
        print("{} actions overall".format(actions_count))
        print("{} bad actions by item".format(bad_actions_by_item_count))
        print("{} bad actions by user".format(bad_actions_by_user_count))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--output-path', type=str, required=True)
    parser.add_argument('--actions-directory', type=str, required=True)
    parser.add_argument('--actions-prefix', type=str, default="circ")
    parser.add_argument('--new-actions-path', type=str, required=True)
    parser.add_argument('--refined-books-path', type=str, required=True)
    parser.add_argument('--refined-users-path', type=str, required=True)
    args = parser.parse_args()
    main(**vars(args))
