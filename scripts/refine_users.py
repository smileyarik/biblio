import argparse

from util import read_csv, write_jsonl

def main(
    output_path,
    readers_file,
    new_actions_file
):
    users_gen = read_csv(
        readers_file,
        encoding="cp1251",
        header=("id", "birth_date", "address")
    )
    users = []
    max_user_id = 0
    for u in users_gen:
        user = {
            "id": int(u["id"]),
            "type": "biblio",
            "meta": {
                "birth_date": u["birth_date"],
                "address": u["address"],
            }
        }
        max_user_id = max(max_user_id, user["id"])
        users.append(user)

    for a in read_csv(new_actions_file):
        user = {
            "id": int(a["user_id"]) + max_user_id,
            "type": "site",
            "meta": {}
        }
        users.append(user)
    users = {u["id"]: u for u in users}
    users = list(users.values())
    users.sort(key=lambda x: x["id"])
    write_jsonl(output_path, users)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--output-path', type=str, required=True)
    parser.add_argument('--readers-file', type=str, required=True)
    parser.add_argument('--new-actions-file', type=str, required=True)
    args = parser.parse_args()
    main(**vars(args))
