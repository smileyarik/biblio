import argparse
import os

from tqdm import tqdm
from util import read_jsonl, write_jsonl


def main(
    input_directory,
    items_path,
    fixture_path
):
    items = read_jsonl(os.path.join(input_directory, items_path))
    seen_scf_ids = set()

    django_items = []
    for item in tqdm(items):
        scf_id = item["scf_id"]
        if scf_id in seen_scf_ids:
            continue
        seen_scf_ids.add(scf_id)
        if author := item["author"]:
            author_name = author["name"][:512]
        django_item = {
            "model": "recsys.book",
            "pk": scf_id,
            "fields": {
                "title": item["title"],
                "author": author_name,
                "id": scf_id,
                "book_id": item["id"]
            }
        }
        django_items.append(django_item)
    write_jsonl(os.path.join(input_directory, fixture_path), django_items)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--input-directory', type=str, required=True)
    parser.add_argument('--items-path', type=str, required=True)
    parser.add_argument('--fixture-path', type=str, required=True)
    args = parser.parse_args()
    main(**vars(args))
