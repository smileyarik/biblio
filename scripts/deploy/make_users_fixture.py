import argparse
import os

from util import read_jsonl, write_jsonl


def main(
    input_directory,
    actions_path,
    fixture_path,
    nrows
):
    actions = read_jsonl(os.path.join(input_directory, actions_path))
    user_ids = set(map(lambda action: action["user_id"], actions))

    django_items = []
    for user_id in user_ids:
        django_item = {
            "model": "recsys.user",
            "pk": user_id,
            "fields": {
                "id": user_id,
            }
        }
        django_items.append(django_item)
    django_items += [{"model": "recsys.user", "pk": 0, "fields": {"id": 0}}]

    write_jsonl(os.path.join(input_directory, fixture_path), django_items)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--input-directory', type=str, required=True)
    parser.add_argument('--actions-path', type=str, required=True)
    parser.add_argument('--fixture-path', type=str, required=True)
    parser.add_argument('--nrows', type=int, default=None)
    args = parser.parse_args()
    main(**vars(args))
