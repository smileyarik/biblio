import argparse
from itertools import islice
from datetime import datetime

from util import read_jsonl, write_jsonl


def main(
    input_path,
    output_path,
    nrows
):
    actions = read_jsonl(input_path)
    django_items = []
    for action in islice(actions, 0, nrows):
        if action["has_bad_user"] or action["has_bad_item"]:
            continue
        django_item = {
            "model": "recsys.action",
            "pk": action["id"],
            "fields": {
                "id": action["id"],
                "book": action["item_id"],
                "user": action["user_id"],
                "type": action["type"],
                "time": datetime.fromtimestamp(action["ts"]).strftime("%Y-%m-%dT%H:%M:%S")
            }
        }
        django_items.append(django_item)

    write_jsonl(output_path, django_items)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('input_path', type=str)
    parser.add_argument('output_path', type=str)
    parser.add_argument('--nrows', type=int, default=None)
    args = parser.parse_args()
    main(**vars(args))
    args = parser.parse_args()
    main(**vars(args))
