import argparse
import datetime
import os
import pickle
from collections import defaultdict

from tqdm import tqdm

from ml.profiles import OT, CT, RT, Profile
from util import read_jsonl


def set_feature_counter(profile, feature, object_type):
    if feature_id := feature['id']:
        profile.counters.set(object_type, CT.HAS, RT.SUM, feature_id, 1, 0)


def make_item_profile(item):
    item_profile = Profile(item["uniq_id"], OT.ITEM)

    if author := item["author"]:
        set_feature_counter(item_profile, author, OT.AUTHOR)

    meta = item["meta"]
    for rubric in meta.get("rubrics", []):
        set_feature_counter(item_profile, rubric, OT.RUBRIC)
    for serial in meta.get("series", []):
        set_feature_counter(item_profile, serial, OT.SERIES)

    return item_profile


def make_user_profile(user, current_ts):
    user_profile = Profile(user["id"], OT.USER)

    if birth_date := user["meta"].get("birth_date"):
        birth_date_ts = datetime.datetime.fromisoformat(birth_date).timestamp()
        user_profile.counters.set(OT.AGE, CT.VALUE, RT.SUM, '', current_ts - birth_date_ts, 0)

    return user_profile


def main(
    input_directory,
    items_path,
    users_path,
    profile_actions_path,
    target_actions_path,
    item_profiles_path,
    user_profiles_path,
    make_for_all
):
    item_profiles = dict()
    user_profiles = dict()

    target_user_ids = set()
    target_min_ts = int(1e10)

    print("Read target users")
    target_action_gen = read_jsonl(os.path.join(input_directory, target_actions_path))
    for action in tqdm(target_action_gen):
        target_user_ids.add(action["user_id"])
        target_min_ts = min(target_min_ts, action["ts"])

    print("Read books data")
    item_gen = read_jsonl(os.path.join(input_directory, items_path))
    for item in tqdm(item_gen):
        item_profiles[item["uniq_id"]] = make_item_profile(item)

    print("Read user data")
    user_gen = read_jsonl(os.path.join(input_directory, users_path))
    for user in tqdm(user_gen):
        user_profiles[user["id"]] = make_user_profile(user, target_min_ts)

    print("Parsing transactions")
    profile_action_gen = read_jsonl(os.path.join(input_directory, profile_actions_path))
    for action in tqdm(profile_action_gen):
        user_id = action["user_id"]
        item_id = action["item_uniq_id"]
        ts = action["ts"]
        assert user_id in user_profiles
        assert item_id in item_profiles
        user_profile = user_profiles[user_id]
        item_profile = item_profiles[item_id]

        for rt in [RT.SUM, RT.D7, RT.D30]:
            item_profile.counters.add(OT.GLOBAL, CT.BOOKING, rt, '', 1, ts)
            if user_id not in target_user_ids and not make_for_all:
                continue

            user_profile.counters.add(OT.GLOBAL, CT.BOOKING, rt, '', 1, ts)
            user_profile.counters.update_from(item_profile.counters, OT.AUTHOR, CT.HAS, RT.SUM, CT.BOOKING_BY, rt, ts)
            user_profile.counters.update_from(item_profile.counters, OT.RUBRIC, CT.HAS, RT.SUM, CT.BOOKING_BY, rt, ts)
            user_profile.counters.update_from(item_profile.counters, OT.SERIES, CT.HAS, RT.SUM, CT.BOOKING_BY, rt, ts)

    item_profiles[3340].print_debug()
    user_profiles[10160192].print_debug()

    print("Dumping user profiles")
    with open(os.path.join(input_directory, user_profiles_path), "w") as w:
        for user_id, user_profile in user_profiles.items():
            if user_id not in target_user_ids and not make_for_all:
                continue
            user_profile.dump(w)

    print("Dumping item profiles")
    with open(os.path.join(input_directory, item_profiles_path), "w") as w:
        for _, item_profile in item_profiles.items():
            item_profile.dump(w)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--input-directory', type=str, required=True)
    parser.add_argument('--items-path', type=str, default="items.jsonl")
    parser.add_argument('--users-path', type=str, default="users.jsonl")
    parser.add_argument('--profile-actions-path', type=str, required=True)
    parser.add_argument('--target-actions-path', type=str, required=True)
    parser.add_argument('--item-profiles-path', type=str, required=True)
    parser.add_argument('--user-profiles-path', type=str, required=True)
    parser.add_argument('--make-for-all', action="store_true", default=False)
    args = parser.parse_args()
    main(**vars(args))

