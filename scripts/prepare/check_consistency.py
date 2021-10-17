import argparse

#import plotext as plt

from tqdm import tqdm

from util import read_jsonl


def main(items_path, users_path, actions_path):
    users = {user["id"]: user for user in read_jsonl(users_path)}
    assert len(users) > 100

    items = {item["id"]: item for item in read_jsonl(items_path)}
    assert len(items) > 100

    uniq_ids = set()
    collapse_fields = set()
    smart_collapse_fields = set()
    for _, item in tqdm(items.items()):
        assert item["uniq_id"] is not None
        assert "meta" in item
        uniq_ids.add(item["uniq_id"])
        if cf := item["meta"].get("collapse_field", None):
            collapse_fields.add(cf)
        if scf := item["meta"].get("smart_collapse_field", None):
            smart_collapse_fields.add(scf)
    print("{} uniq ids".format(len(uniq_ids)))
    assert len(uniq_ids) > 0
    print("{} collapse fields".format(len(collapse_fields)))
    assert len(collapse_fields) > 0
    print("{} smart collapse fields".format(len(smart_collapse_fields)))
    assert len(smart_collapse_fields) > 0

    actions_count = 0
    for action in tqdm(read_jsonl(actions_path)):
        assert action["user_id"] in users or action["has_bad_user"]
        assert action["item_id"] in items or action["has_bad_item"]
        actions_count += 1
    assert actions_count >= 10000

    print("ALL OK")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--items-path', type=str, required=True)
    parser.add_argument('--users-path', type=str, required=True)
    parser.add_argument('--actions-path', type=str, required=True)
    args = parser.parse_args()
    main(**vars(args))
