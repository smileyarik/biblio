import argparse
import os
import string
from itertools import chain
from collections import defaultdict

from tqdm import tqdm

from util import read_csv_files, write_jsonl, read_jsonl, read_json


def read_feature_to_id(
    directory,
    pattern,
    feature
):
    gen = read_csv_files(
        directory=directory,
        pattern=pattern,
        encoding="cp1251"
    )
    return {a[feature] : int(a["id"]) for a in gen}


def process_biblio_feature(value, mapping):
    return {"id": mapping.get(value), "name": value} if value else None


def process_biblio_features(values, separator, mapping):
    return [process_biblio_feature(value, mapping) for value in values.split(separator) if value]


def process_site_feature(feature_id, name):
    if not feature_id or not name:
        return None
    return {"id": feature_id, "name": name}


def main(
    input_directory,
    items_pattern,
    authors_pattern,
    persons_pattern,
    rubrics_pattern,
    series_pattern,
    site_items_path,
    site_small_items_path,
    output_path
):
    print("Reading biblio/authors...")
    author_to_id = read_feature_to_id(input_directory, authors_pattern, "author")
    print("... {} biblio/authors read".format(len(author_to_id)))

    print("Reading biblio/rubrics...")
    rubric_to_id = read_feature_to_id(input_directory, rubrics_pattern, "rubrics")
    print("... {} biblio/rubrics read".format(len(rubric_to_id)))

    print("Reading biblio/series...")
    serial_to_id = read_feature_to_id(input_directory, series_pattern, "serial")
    print("... {} biblio/series read".format(len(serial_to_id)))

    print("Reading biblio/persons...")
    person_to_id = read_feature_to_id(input_directory, persons_pattern, "person")
    print("... {} biblio/persons read".format(len(person_to_id)))

    print("Reading biblio/items...")
    items_gen = read_csv_files(
        directory=input_directory,
        pattern=items_pattern,
        encoding="cp1251"
    )

    items = []
    for r in tqdm(items_gen):
        record = {
            "author": process_biblio_feature(r.pop("aut"), author_to_id),
            "title": r.pop("title"),
            "id": int(r.pop("recId")),
            "meta": {
                "is_candidate": False,
                "is_site": False,
                "place": r.pop("place"),
                "publisher": r.pop("publ"),
                "year": r.pop("yea"),
                "language": r.pop("lan"),
                "rubrics": process_biblio_features(r.pop("rubrics"), " : ", rubric_to_id),
                "series": process_biblio_features(r.pop("serial"), " : ", serial_to_id),
                "type": r.pop("material"),
                "age_rating": r.pop("ager"),
                "persons": process_biblio_features(r.pop("person"), (" , "), person_to_id),
                "level": r.pop("biblevel"),
            }
        }
        for key, value in list(record["meta"].items()):
            if value == '' or value == [''] or value is None:
                record["meta"].pop(key)
        if not record["id"]:
            continue
        if not record["title"]:
            continue
        items.append(record)

    items = {r["id"]: r for r in items}
    print("... {} biblio/items read".format(len(items)))

    print("Reading site/items...")

    small_site_items = list(read_json(os.path.join(input_directory, site_small_items_path)))
    for item in small_site_items:
        item["is_candidate"] = True

    site_items = read_jsonl(os.path.join(input_directory, site_items_path))
    for r in tqdm(chain(small_site_items, site_items)):
        rubric = process_site_feature(r.pop("rubric_id"), r.pop("rubric_name"))
        serial = process_site_feature(r.pop("serial_id"), r.pop("serial_name"))

        record = {
            "author": process_site_feature(r.pop("author_id"), r.pop("author_fullName")),
            "id": int(r.pop("id")),
            "title": r.pop("title"),
            "meta": {
                "is_candidate": ("is_candidate" in r),
                "is_site": True,
                "place": r.pop("place_name"),
                "publisher": r.pop("publisher_name"),
                "year": r.pop("year_value"),
                "rubrics": [rubric] if rubric else [],
                "series": [serial] if serial else [],
                "isbn": r.pop("isbn"),
                "annotation": r.pop("annotation"),
                "collapse_field": r.pop("collapse_field"),
                "smart_collapse_field": r.pop("smart_collapse_field")
            }
        }
        for key, value in list(record["meta"].items()):
            if value == '' or value == [''] or value is None:
                record["meta"].pop(key)
        rid = record["id"]
        if rid in items:
            items[rid]["meta"].update(record["meta"])
            continue
        items[rid] = record
    print("... {} items read overall".format(len(items)))

    print("Calculating uniq_id...")
    buckets = defaultdict(list)
    for _, item in items.items():
        title = item["title"].lower()
        author = ""
        if item["author"] and "name" in item["author"]:
            author = item["author"]["name"].lower()

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
    print("... {} buckets".format(len(buckets)))

    print("Writing to {}...".format(output_path))
    items_plain = list(items.values())
    items_plain.sort(key=lambda x: x["uniq_id"])
    write_jsonl(output_path, items_plain)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--input-directory', type=str, required=True)
    parser.add_argument('--items-pattern', type=str, default="cat_*.csv")
    parser.add_argument('--authors-pattern', type=str, default="authors.csv")
    parser.add_argument('--persons-pattern', type=str, default="persons.csv")
    parser.add_argument('--rubrics-pattern', type=str, default="rubrics.csv")
    parser.add_argument('--series-pattern', type=str, default="series.csv")
    parser.add_argument('--site-items-path', type=str, default="all_books.jsonl")
    parser.add_argument('--site-small-items-path', type=str, default="items.json")
    parser.add_argument('--output-path', type=str, required=True)
    args = parser.parse_args()
    main(**vars(args))
