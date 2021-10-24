import argparse

from tqdm import tqdm

from util import read_jsonl


def main(items_path, users_path, actions_path):
    users = {user["id"]: user for user in read_jsonl(users_path)}
    assert len(users) > 100

    items = {item["id"]: item for item in read_jsonl(items_path)}
    assert len(items) > 100

    multiple_rubrics_count = 0
    multiple_series_count = 0
    smart_collapse_fields = set()
    for _, item in tqdm(items.items()):
        assert "meta" in item
        meta = item["meta"]
        assert item.get("scf_id")
        scf = item["scf_id"]
        smart_collapse_fields.add(scf)
        if len(meta.get("rubrics", [])) > 1:
            multiple_rubrics_count += 1
        if len(meta.get("series", [])) > 1:
            multiple_series_count += 1

    print("{} items with multiple rubrics".format(multiple_rubrics_count))
    assert multiple_rubrics_count > 0
    print("{} items with multiple series".format(multiple_series_count))
    assert multiple_series_count > 0
    print("{} smart collapse fields".format(len(smart_collapse_fields)))
    assert len(smart_collapse_fields) > 0

    actions_count = 0
    ts = 0
    for action in tqdm(read_jsonl(actions_path)):
        assert action["user_id"] in users or action["has_bad_user"]
        assert action["item_id"] in items or action["has_bad_item"]
        assert action["ts"] >= ts
        ts = action["ts"]
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
