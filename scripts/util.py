import os
import csv
import json
import random


def read_csv(
    file_name,
    delimiter=";",
    encoding='utf-8-sig',
    save_fields=None,
    sample_rate=1.0
):
    with open(file_name, encoding=encoding) as r:
        reader = csv.reader(r, delimiter=delimiter)
        header = next(reader)
        for row in reader:
            record = dict(zip(header, row))
            record.pop('', None)
            if save_fields:
                record = {k: v for k, v in record.items() if k in save_fields}
            if random.random() < sample_rate:
                yield record


def read_csv_files(
    directory,
    prefix,
    delimiter=";",
    encoding='utf-8-sig',
    save_fields=None,
    sample_rate=1.0
):
    for file_name in os.listdir(directory):
        full_path = os.path.join(directory, file_name)
        assert os.path.exists(full_path)
        if file_name.startswith(prefix):
            file_gen = read_csv(
                file_name=full_path,
                delimiter=delimiter,
                encoding=encoding,
                save_fields=save_fields,
                sample_rate=sample_rate
            )
            for record in file_gen:
                yield record


def write_jsonl(path, items):
    with open(path, "w", encoding="utf-8") as w:
        for item in items:
            w.write(json.dumps(item, ensure_ascii=False).strip() + "\n")


def read_jsonl(path):
    with open(path, "r", encoding="utf-8") as r:
        for line in r:
            yield json.loads(line)


def read_json(path, save_fields=None):
    with open(path) as r:
        records = json.load(r)
        if save_fields:
            records = [{k: v for k, v in r.items() if k in save_fields} for r in records]
    return records

def write_json(path, items):
    with open(path, "w", encoding="utf-8") as w:
        json.dump(items, w, ensure_ascii=False, sort_keys=True, indent=4)
