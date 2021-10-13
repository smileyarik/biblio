import argparse
import string
from collections import defaultdict

from util import read_csv_files, read_json, write_jsonl

def main(
    biblio_directory,
    items_pattern,
    authors_pattern,
    new_items_path,
    output_path
):
    print("Reading biblio/authors...")
    authors_gen = read_csv_files(
        directory=biblio_directory,
        pattern=authors_pattern,
        encoding="cp1251"
    )
    author_to_id = { a['author'] : int(a['id']) for a in authors_gen }
    print("{} biblio/authors processed".format(len(author_to_id)))

    print("Processing main items...")
    items_gen = read_csv_files(
        directory=biblio_directory,
        pattern=items_pattern,
        encoding="cp1251"
    )

    items = []
    for r in items_gen:
        author = r.pop("aut")
        if author == "":
            author = None

        record = {
            "author": author,
            "author_id": author_to_id.get(author, None),
            "title": r.pop("title"),
            "id": int(r.pop("recId")),
            "meta": {
                "place": r.pop("place"),
                "publisher": r.pop("publ"),
                "year": r.pop("yea"),
                "language": r.pop("lan"),
                "rubrics": r.pop("rubrics").split(" : "),
                "series": r.pop("serial").split(" : "),
                "type": r.pop("material"),
                "age_rating": r.pop("ager"),
                "persons": r.pop("person").split(" , "),
                "level": r.pop("biblevel")
            }
        }
        for key, value in list(record["meta"].items()):
            if value == '' or value == ['']:
                record["meta"].pop(key)
        if not record["id"]:
            continue
        if not record["title"]:
            continue
        items.append(record)

    items = {r["id"]: r for r in items}
    print("{} main items processed".format(len(items)))

    print("Processing new items...")
    for r in read_json(new_items_path):
        record = {
            "author": r.pop("author_fullName"),
            "id": int(r.pop("id")),
            "title": r.pop("title"),
            "meta": {
                "place": r.pop("place_name"),
                "publisher": r.pop("publisher_name"),
                "year": r.pop("year_value"),
                "rubrics": r.pop("rubric_name"),
                "isbn": r.pop("isbn"),
                "annotation": r.pop("annotation")
            }
        }
        if record["meta"]["rubrics"]:
            record["meta"]["rubrics"] = record["meta"]["rubrics"].split(" : ")
        for key, value in list(record["meta"].items()):
            if value == '' or value == ['']:
                record["meta"].pop(key)
        rid = record["id"]
        if rid in items:
            items[rid]["meta"].update(record["meta"])
            continue
        items[rid] = record
    print("{} items overall".format(len(items)))

    print("Calculating uniq_id...")
    buckets = defaultdict(list)
    for _, item in items.items():
        title = item["title"].lower()
        author = item["author"].lower() if item["author"] else ""

        orig_key = title + " " + author
        key = orig_key.translate(str.maketrans('', '', string.punctuation))
        key = key.replace(" ", "")
        if len(key) >= 10:
            buckets[key].append(item["id"])
        else:
            buckets[orig_key].append(item["id"])

    for bucket_num, (_, bucket) in enumerate(buckets.items()):
        for item_id in bucket:
            items[item_id]["uniq_id"] = bucket_num
    print("{} buckets".format(len(buckets)))

    print("Writing to {}...".format(output_path))
    items_plain = list(items.values())
    items_plain.sort(key=lambda x: x["uniq_id"])
    write_jsonl(output_path, items_plain)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--output-path', type=str, required=True)
    parser.add_argument('--biblio-directory', type=str, required=True)
    parser.add_argument('--items-pattern', type=str, default="cat_*.csv")
    parser.add_argument('--authors-pattern', type=str, default="authors.csv")
    parser.add_argument('--new-items-path', type=str, required=True)
    args = parser.parse_args()
    main(**vars(args))
