import argparse
import os
import string
from itertools import chain
from collections import defaultdict, Counter

from tqdm import tqdm

from util import read_csv_files, write_jsonl, read_jsonl, read_json, merge_meta
from prepare.tfidf import get_keywords, load_idfs


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
    return {a[feature]: int(a["id"]) for a in gen}


def process_biblio_feature(value, mapping):
    return {"id": mapping.get(value), "name": value} if value else None


def process_biblio_features(values, separator, mapping):
    return [process_biblio_feature(value, mapping) for value in values.split(separator) if value]


def process_site_feature(feature_id, name):
    if not feature_id or not name:
        return None
    return {"id": feature_id, "name": name}


def clean_meta(record):
    for key, value in list(record["meta"].items()):
        if value == '' or value == [''] or value is None or value == []:
            record["meta"].pop(key)


def main(
    input_directory,
    items_pattern,
    authors_pattern,
    languages_pattern,
    persons_pattern,
    rubrics_pattern,
    series_pattern,
    site_items_path,
    site_small_items_path,
    idfs_path,
    output_path
):
    word2idf = None
    if idfs_path:
        print("Reading IDFs...")
        word2idf, word2idx = load_idfs(idfs_path)
        print("... {} word loaded".format(len(word2idf)))

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

    print("Reading biblio/languages...")
    language_to_id = read_feature_to_id(input_directory, languages_pattern, "lan_short")
    print("... {} biblio/languages read".format(len(person_to_id)))

    age_restriction_to_id = {"0+": 6630, "6+": 6634, "12+": 6633, "16+": 6631, "18+": 6632}

    print("Reading biblio/items...")
    items_gen = read_csv_files(
        directory=input_directory,
        pattern=items_pattern,
        encoding="cp1251"
    )

    # TODO: Add BBK
    items = []
    for r in tqdm(items_gen):
        age_restriction = r.pop("ager")
        record = {
            "author": process_biblio_feature(r.pop("aut"), author_to_id),
            "title": r.pop("title"),
            "id": int(r.pop("recId")),
            "meta": {
                "is_candidate": False,
                "age_restriction": age_restriction_to_id[age_restriction] if age_restriction else None,
                "language": process_biblio_features(r.pop("lan"), " , ", language_to_id),
                "persons": process_biblio_features(r.pop("person"), " , ", person_to_id),
                "rubrics": process_biblio_features(r.pop("rubrics"), " : ", rubric_to_id),
                "series": process_biblio_features(r.pop("serial"), " : ", serial_to_id)
            }
        }
        clean_meta(record)
        assert record["id"]
        if not record["title"]:
            continue
        items.append(record)

    items = {r["id"]: r for r in items}
    print("... {} biblio/items read".format(len(items)))

    print("Reading small site/items...")
    small_site_items = list(read_json(os.path.join(input_directory, site_small_items_path)))
    for item in small_site_items:
        item["is_candidate"] = True

    print("Reading big site/items...")
    field_to_id = dict()
    site_items = read_jsonl(os.path.join(input_directory, site_items_path))
    for r in tqdm(chain(small_site_items, site_items)):
        rubric = process_site_feature(r.pop("rubric_id"), r.pop("rubric_name"))
        serial = process_site_feature(r.pop("serial_id"), r.pop("serial_name"))
        language = process_site_feature(r.pop("language_id"), r.pop("language_name"))
        smart_collapse_field = r.pop("smart_collapse_field")
        assert smart_collapse_field
        if smart_collapse_field not in field_to_id:
            field_to_id[smart_collapse_field] = len(field_to_id)
        record = {
            "author": process_site_feature(r.pop("author_id"), r.pop("author_fullName")),
            "id": int(r.pop("id")),
            "title": r.pop("title"),
            "scf_id": field_to_id[smart_collapse_field],
            "meta": {
                "is_candidate": ("is_candidate" in r),
                "smart_collapse_field": smart_collapse_field,
                "age_restriction": r.pop("ageRestriction_id"),
                "annotation": r.pop("annotation"),
                "bbk": r.pop("bbk"),
                "language": [language] if language else [],
                "rubrics": [rubric] if rubric else [],
                "series": [serial] if serial else [],
                "type": r.pop("material_id")
            }
        }

        annotation = record["meta"].pop("annotation", None)
        if word2idf and annotation:
            annotation = " ".join(annotation.split()[:200])
            record["meta"]["keywords"] = get_keywords(annotation, word2idf, word2idx, k=5)
            record["meta"]["keywords"] += get_keywords(record["title"], word2idf, word2idx, k=2)

        clean_meta(record)
        assert record["id"]
        if not record["title"]:
            continue

        rid = record["id"]
        if r.pop("deleted", False):
            if rid in items:
                items.pop(rid)
            continue

        if rid not in items:
            items[rid] = record
            continue

        old_record = items[rid]
        old_meta = old_record["meta"]
        new_meta = record["meta"]
        old_record["scf_id"] = record["scf_id"]
        merged_meta = merge_meta(old_meta, new_meta, ("language", "rubrics", "series"))
        is_candidate = old_meta.get("is_candidate", False) or new_meta.get("is_candidate", False)
        old_meta.update(new_meta)
        old_meta["is_candidate"] = is_candidate
        for field, features in merged_meta.items():
            old_meta[field] = features
        clean_meta(old_record)

    items = {rid: item for rid, item in items.items() if item.get("scf_id")}
    print("... {} items read overall".format(len(items)))

    print("Writing to {}...".format(output_path))
    items_plain = list(items.values())
    items_plain.sort(key=lambda x: (x["scf_id"], x["id"]))
    write_jsonl(output_path, items_plain)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--input-directory', type=str, required=True)
    parser.add_argument('--items-pattern', type=str, default="cat_*.csv")
    parser.add_argument('--authors-pattern', type=str, default="authors.csv")
    parser.add_argument('--languages-pattern', type=str, default="languages.csv")
    parser.add_argument('--persons-pattern', type=str, default="persons.csv")
    parser.add_argument('--rubrics-pattern', type=str, default="rubrics.csv")
    parser.add_argument('--series-pattern', type=str, default="series.csv")
    parser.add_argument('--site-items-path', type=str, default="all_books.jsonl")
    parser.add_argument('--site-small-items-path', type=str, default="items.json")
    parser.add_argument('--idfs-path', type=str, default=None)
    parser.add_argument('--output-path', type=str, required=True)
    args = parser.parse_args()
    main(**vars(args))
