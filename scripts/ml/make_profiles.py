import argparse
import datetime
import os
import pickle
from collections import defaultdict

from tqdm import tqdm

from ml.bbk_processor import BbkProcessor
from ml.profiles import OT, CT, RT, Profile
from util import read_jsonl, is_site_user, merge_meta


# reader age statistics in item profile is stored as histogram with bins of size below (in years)
READER_AGE_HISTOGRAM_BIN = 5


def set_repeated_feature_counter(profile, feature, object_type):
    if feature_id := feature['id']:
        profile.counters.set(object_type, CT.HAS, RT.SUM, feature_id, 1, 0)


def set_single_feature_counter(profile, value, object_type):
    if value:
        profile.counters.set(object_type, CT.HAS, RT.SUM, value, 1, 0)


def make_item_profile(item, bbk_processor):
    item_profile = Profile(item["scf_id"], OT.ITEM)

    if author := item["author"]:
        set_repeated_feature_counter(item_profile, author, OT.AUTHOR)

    meta = item["meta"]
    for rubric in meta.get("rubrics", []):
        set_repeated_feature_counter(item_profile, rubric, OT.RUBRIC)
    for serial in meta.get("series", []):
        set_repeated_feature_counter(item_profile, serial, OT.SERIES)
    for language in meta.get("language", []):
        set_repeated_feature_counter(item_profile, language, OT.LANGUAGE)
    for keyword in meta.get("keywords", []):
        set_single_feature_counter(item_profile, keyword, OT.KEYWORD)
    if bbk_str := meta.get("bbk"):
        for bbk in bbk_processor.parse_str(bbk_str):
            for bbk_prefix in bbk_processor.get_all_prefixes(bbk):
                set_single_feature_counter(item_profile, bbk_prefix, OT.BBK_PREFIX)

    set_single_feature_counter(item_profile, meta.get("age_restriction"), OT.AGE_RESTRICTION)

    return item_profile


def make_user_profile(user):
    user_profile = Profile(user["id"], OT.USER)

    if birth_date := user["meta"].get("birth_date"):
        birth_date_ts = datetime.datetime.fromisoformat(birth_date).timestamp()
        user_profile.counters.set(OT.AGE, CT.VALUE, RT.SUM, '', birth_date_ts, 0)

    return user_profile


def merge_items(item1, item2):
    if item1 is None:
        return item2
    if item2 is None:
        return item1

    meta1 = item1["meta"]
    meta2 = item2["meta"]
    assert item1["scf_id"] == item2["scf_id"]
    merged_meta = merge_meta(meta1, meta2, ("rubrics", "series", "keywords"))
    item = {
        "author": item1["author"],
        "title": item1["title"],
        "scf_id": item1["scf_id"],
        "meta": {
            "rubrics": merged_meta["rubrics"],
            "series": merged_meta["series"],
            "keywords": merged_meta["keywords"]
        }
    }
    return item


def main(
    input_directory,
    items_path,
    users_path,
    profile_actions_path,
    target_actions_path,
    make_for_site,
    item_profiles_path,
    user_profiles_path,
    bbk_path
):
    item_profiles = dict()
    user_profiles = dict()
    target_user_ids = set()

    print("Init BBK Processor")
    bbk_processor = BbkProcessor(bbk_path)

    print("Read target users")
    if target_actions_path:
        target_action_gen = read_jsonl(os.path.join(input_directory, target_actions_path))
        for action in tqdm(target_action_gen):
            target_user_ids.add(action["user_id"])
    else:
        print("... omitted")

    def _is_target_user(user_id):
        if make_for_site:
            return is_site_user(user_id)
        return not target_user_ids or user_id in target_user_ids

    print("Read books data")
    item_gen = read_jsonl(os.path.join(input_directory, items_path))
    items = dict()
    for item in tqdm(item_gen):
        scf_id = item["scf_id"]
        items[scf_id] = merge_items(items.get(scf_id, None), item)

    for scf_id, item in tqdm(items.items()):
        item_profiles[scf_id] = make_item_profile(item, bbk_processor)
    del items

    print("Read user data")
    user_gen = read_jsonl(os.path.join(input_directory, users_path))
    for user in tqdm(user_gen):
        user_profiles[user["id"]] = make_user_profile(user)

    print("Parsing transactions #1")
    profile_action_gen = read_jsonl(os.path.join(input_directory, profile_actions_path))
    for action in tqdm(profile_action_gen):
        user_id = action["user_id"]
        item_id = action["item_scf"]
        ts = action["ts"]
        assert user_id in user_profiles
        assert item_id in item_profiles
        user_profile = user_profiles[user_id]
        item_profile = item_profiles[item_id]

        if user_birth_ts := user_profile.counters.get(OT.AGE, CT.VALUE, RT.SUM, '', 0):
            if ts > user_birth_ts:
                user_age_days = datetime.timedelta(seconds=ts-user_birth_ts).days
                user_age_group = int(user_age_days // (READER_AGE_HISTOGRAM_BIN * 365))
                item_profile.counters.add(OT.READER_AGE, CT.BOOKING, RT.SUM, str(user_age_group), 1, ts)

        for rt in [RT.SUM, RT.D7, RT.D30]:
            item_profile.counters.add(OT.GLOBAL, CT.BOOKING, rt, '', 1, ts)
            if not _is_target_user(user_id):
                continue

            user_profile.counters.add(OT.GLOBAL, CT.BOOKING, rt, '', 1, ts)

            def update_from(from_ot, from_ct, from_rt, to_ct):
                user_profile.counters.update_from(item_profile.counters, from_ot, from_ct, from_rt, to_ct, rt, ts)

            update_from(OT.AUTHOR, CT.HAS, RT.SUM, CT.BOOKING_BY)
            update_from(OT.RUBRIC, CT.HAS, RT.SUM, CT.BOOKING_BY)
            update_from(OT.SERIES, CT.HAS, RT.SUM, CT.BOOKING_BY)
            update_from(OT.KEYWORD, CT.HAS, RT.SUM, CT.BOOKING_BY)
            update_from(OT.AGE_RESTRICTION, CT.HAS, RT.SUM, CT.BOOKING_BY)
            update_from(OT.LANGUAGE, CT.HAS, RT.SUM, CT.BOOKING_BY)
            update_from(OT.BBK_PREFIX, CT.HAS, RT.SUM, CT.BOOKING_BY)

    print("Normalize item profiles")
    for _, item_profile in item_profiles.items():
        total_bookings = item_profile.counters.get(OT.GLOBAL, CT.BOOKING, RT.SUM, '', 0)
        user_age_counters = item_profile.counters.slice(OT.READER_AGE, CT.BOOKING, RT.SUM)
        for _, user_age_counter in user_age_counters.items():
            user_age_counter.value = user_age_counter.value / total_bookings

    print("Parsing transactions #2")
    profile_action_gen = read_jsonl(os.path.join(input_directory, profile_actions_path))
    for action in tqdm(profile_action_gen):
        user_id = action["user_id"]
        item_id = action["item_scf"]
        ts = action["ts"]
        assert user_id in user_profiles
        assert item_id in item_profiles
        user_profile = user_profiles[user_id]
        item_profile = item_profiles[item_id]

        if not _is_target_user(user_id):
            continue

        for rt in [RT.SUM, RT.D7, RT.D30]:
            user_profile.counters.update_from(
                item_profile.counters, OT.READER_AGE, CT.BOOKING,
                RT.SUM, CT.BOOKING_BY, rt, ts
            )

    item_profiles[1337].print_debug()
    user_profiles[1].print_debug()

    print("Dumping user profiles")
    with open(os.path.join(input_directory, user_profiles_path), "w") as w:
        for user_id, user_profile in user_profiles.items():
            if not _is_target_user(user_id):
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
    parser.add_argument('--target-actions-path', type=str, required=False)
    parser.add_argument('--make-for-site', action="store_true", default=False)
    parser.add_argument('--item-profiles-path', type=str, required=True)
    parser.add_argument('--user-profiles-path', type=str, required=True)
    parser.add_argument('--bbk-path', type=str, default="ml/bbk_mapping.json")
    args = parser.parse_args()
    main(**vars(args))
