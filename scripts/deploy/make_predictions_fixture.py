import argparse
import os

from tqdm import tqdm
from util import read_jsonl, write_jsonl


def main(
    input_directory,
    predictions_path,
    fixture_path,
    nrows
):
    predictions = []
    with open(os.path.join(input_directory, predictions_path)) as r:
        for line in tqdm(r):
            user_id, item_id, _, score = line.strip().split("\t")
            predictions.append((int(user_id), int(item_id), float(score)))

    django_items = []
    for i, (user_id, item_id, score) in enumerate(predictions):
        django_item = {
            "model": "recsys.recommendation",
            "pk": i,
            "fields": {
                "id": i,
                "book": item_id,
                "user": user_id,
                "score": score
            }
        }
        django_items.append(django_item)

    write_jsonl(os.path.join(input_directory, fixture_path), django_items)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--input-directory', type=str, required=True)
    parser.add_argument('--predictions-path', type=str, required=True)
    parser.add_argument('--fixture-path', type=str, required=True)
    parser.add_argument('--nrows', type=int, default=None)
    args = parser.parse_args()
    main(**vars(args))
