import glob
import os
import csv
import json
import random
import datetime


def read_csv(
    file_name,
    delimiter=";",
    encoding='utf-8-sig',
    save_fields=None,
    sample_rate=1.0,
    header=None
):
    with open(file_name, encoding=encoding) as r:
        reader = csv.reader(r, delimiter=delimiter)
        if header is None:
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
    pattern,
    delimiter=";",
    encoding='utf-8-sig',
    save_fields=None,
    sample_rate=1.0
):
    for file_name in glob.iglob(os.path.join(directory, pattern)):
        file_gen = read_csv(
            file_name=file_name,
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


def datetime_to_ts(dt):
    return int(datetime.datetime.strptime(dt, '%Y-%m-%d %H:%M:%S').timestamp())


def date_to_ts(dt):
    return int(datetime.datetime.strptime(dt, '%d.%m.%Y').timestamp())
