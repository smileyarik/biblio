import argparse
from util import read_jsonl, write_jsonl


def main(
    input_path,
    output_path
):
    items = read_jsonl(input_path)
    django_items = []
    for item in items:
        django_item = {
            "model": "recsys.user",
            "pk": item["id"],
            "fields": {
                "id": item["id"],
            }
        }
        django_items.append(django_item)
    write_jsonl(output_path, django_items)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('input_path', type=str)
    parser.add_argument('output_path', type=str)
    args = parser.parse_args()
    main(**vars(args))
