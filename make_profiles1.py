import argparse
import datetime
import os
import pickle

from collections import defaultdict
from profiles import *
from tqdm import tqdm
from scripts.util import read_jsonl


def make_item_profile(item):
    item_profile = Counters()

    def _set_feature_counter(item, feature, object_type):
        if feature_id := feature['id']:
            item.set(object_type, CT_HAS, RT_SUM, feature_id, 1, 0)

    if author := item["author"]:
        _set_feature_counter(item_profile, author, OT_AUTHOR)

    meta = item["meta"]
    for rubric in meta.get("rubrics", []):
        _set_feature_counter(item_profile, rubric, OT_RUBRIC)

    for person in meta.get("persons", []):
        _set_feature_counter(item_profile, person, OT_PERSON)

    for serial in meta.get("series", []):
        _set_feature_counter(item_profile, serial, OT_SERIES)

    if library_availability := item["meta"].get("library_availability"):
        for library in library_availability:
            item_profile.set(OT_LIBRARY, CT_VALUE, RT_SUM, library["id"], library["count"], 0)

    return item_profile


def make_user_profile(user, current_ts):
    user_profile = Counters()

    if birth_date := user["meta"].get("birth_date"):
        birth_date_ts = datetime.datetime.fromisoformat(birth_date).timestamp()
        user_profile.set(OT_AGE, CT_VALUE, RT_SUM, '', current_ts - birth_date_ts, 0)

    return user_profile


def main(
    input_directory,
    items_path,
    users_path,
    profile_actions_path,
    target_actions_path,
    output_directory,
    item_profiles_path,
    user_profiles_path
):
    item_profiles = defaultdict(lambda: Counters())
    user_profiles = defaultdict(lambda: Counters())

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
        item_profiles[item["id"]] = make_item_profile(item)

    print("Read user data")
    user_gen = read_jsonl(os.path.join(input_directory, users_path))
    for user in tqdm(user_gen):
        user_profiles[user["id"]] = make_user_profile(user, target_min_ts)

    print("Parsing transactions")
    profile_action_gen = read_jsonl(os.path.join(input_directory, profile_actions_path))
    for action in tqdm(profile_action_gen):
        user_id = action["user_id"]
        item_id = action["item_id"]
        ts = action["ts"]

        user_profile = user_profiles[user_id]
        item_profile = item_profiles[item_id]

        for rt in [RT_SUM, RT_7D, RT_30D]:
            item_profile.add(OT_GLOBAL, CT_BOOKING, rt, '', 1, ts)
#            if library_id != None:
#                item.add(OT_LIBRARY, CT_BOOKING, rt, library_id, 1, ts)
#            # TODO calc age stat for book
#            item.update_from(user, OT_AGE, CT_HAS, RT_SUM, CT_REVIEW_BY, rt, ts)

            if user_id not in target_user_ids:
                continue

            user_profile.add(OT_GLOBAL, CT_BOOKING, rt, '', 1, ts)

#            if library_id != None:
#                user.add(OT_LIBRARY, CT_BOOKING, rt, library_id, 1, ts)

            user_profile.update_from(item_profile, OT_AUTHOR, CT_HAS, RT_SUM, CT_BOOKING_BY, rt, ts)
            user_profile.update_from(item_profile, OT_RUBRIC, CT_HAS, RT_SUM, CT_BOOKING_BY, rt, ts)
            user_profile.update_from(item_profile, OT_PERSON, CT_HAS, RT_SUM, CT_BOOKING_BY, rt, ts)
            user_profile.update_from(item_profile, OT_SERIES, CT_HAS, RT_SUM, CT_BOOKING_BY, rt, ts)


    print('==========================')
    item_profiles[456976].print_debug()


    print("Dumping user profiles")
    user_profiles = { k: v for k, v in user_profiles.items() if k in target_user_ids }
    with open(os.path.join(output_directory, user_profiles_path), 'wb') as user_profiles_pickle:
        pickle.dump(user_profiles, user_profiles_pickle)

    print("Dumping item profiles")
    with open(os.path.join(output_directory, item_profiles_path), 'wb') as item_profiles_pickle:
        pickle.dump(dict(item_profiles), item_profiles_pickle)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--input-directory', type=str, required=True)
    parser.add_argument('--items-path', type=str, default="items.jsonl")
    parser.add_argument('--users-path', type=str, default="users.jsonl")
    parser.add_argument('--profile-actions-path', type=str, required=True)
    parser.add_argument('--target-actions-path', type=str, required=True)
    parser.add_argument('--output-directory', type=str, required=True)
    parser.add_argument('--item-profiles-path', type=str, default="item_profiles.pkl")
    parser.add_argument('--user-profiles-path', type=str, default="user_profiles.pkl")
    args = parser.parse_args()
    main(**vars(args))
