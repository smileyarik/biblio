import argparse
from util import read_jsonl, write_json


def main(
    input_path,
    output_path
):
    items = read_jsonl(input_path)
    django_items = []
    for item in items:
        django_item = {
            "model": "recsys.book",
            "pk": item["id"],
            "fields": {
                "title": item["title"],
                "author": item["author"],
                "id": item["id"],
                "uniq_id": item["uniq_id"]
            }
        }
        django_items.append(django_item)
    write_json(output_path, django_items[:1000])


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('input_path', type=str)
    parser.add_argument('output_path', type=str)
    args = parser.parse_args()
    main(**vars(args))
