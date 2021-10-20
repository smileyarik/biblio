import argparse
import pickle
import os
from collections import defaultdict

from tqdm import tqdm

from ml.profiles import OT, CT, RT, Counters, Profile
from ml.features_lib import ColumnDescription, counter_cos, FeaturesCalcer
from util import read_jsonl, is_site_user


def main(
    input_directory,
    item_profiles_path,
    user_profiles_path,
    target_actions_path,
    poptop,
    items_per_group,
    start_ts,
    profile_actions_path,
    features_output_path,
    cd_output_path,
    rw_path
):
    print("Read user profiles")
    users = dict()
    with open(os.path.join(input_directory, user_profiles_path), "r") as r:
        for line in tqdm(r):
            profile = Profile.loads(line)
            users[profile.object_id] = profile
    print("...{} users read".format(len(users)))

    print("Read item profiles")
    items = dict()
    with open(os.path.join(input_directory, item_profiles_path), "r") as r:
        for line in tqdm(r):
            profile = Profile.loads(line)
            items[profile.object_id] = profile
    print("...{} items read".format(len(items)))

    print("Read target users")
    target_users = set()
    target_items = defaultdict(set)
    target_actions = read_jsonl(os.path.join(input_directory, target_actions_path))
    for action in tqdm(target_actions):
        target_users.add(action["user_id"])
        target_items[action["user_id"]].add(action["item_scf"])
    print("...{} target users".format(len(target_users)))

    print("Read already seen items")
    filter_items = defaultdict(set)
    stat_actions = read_jsonl(os.path.join(input_directory, profile_actions_path))
    for action in tqdm(stat_actions):
        filter_items[action["user_id"]].add(action["item_scf"])

    print("Random walk load")
    rw_records = read_jsonl(os.path.join(input_directory, rw_path))
    rw_graph = defaultdict(lambda: defaultdict(float))
    for record in rw_records:
        rw_graph[record["user"]][record["item"]] = record["weight"]

    print("Calc candidates")
    book_top = []
    for item_id, item in items.items():
        item_size = float(item.counters.get(OT.GLOBAL, CT.BOOKING, RT.D30, '', start_ts))
        book_top.append((item_id, item_size))
    book_top = sorted(book_top, key=lambda x:-x[1])

    print("Calc global stat")
    full_events = Counters()
    for item_id, item in items.items():
        for rt in [RT.SUM, RT.D7, RT.D30]:
            full_events.update_from(item.counters, OT.GLOBAL, CT.BOOKING, rt, CT.BOOKING, rt, start_ts)

    print('All bookings 30d:', full_events.get(OT.GLOBAL, CT.BOOKING, RT.D30, '', start_ts))

    print("Calc features")
    calcer = FeaturesCalcer(rw_graph, full_events)
    features_output = open(os.path.join(input_directory, features_output_path), "w")

    bad_candidates_count = 0
    for user_id in tqdm(target_users):
        user = users[user_id]
        user_counters = user.counters.slice(OT.GLOBAL, CT.BOOKING, RT.SUM)
        user_last_ts = start_ts
        if counter := user_counters.get("", None):
            user_last_ts = counter.ts

        top = {item_id for item_id, _ in book_top[:poptop]}

        rw_top = [(item_id, value) for item_id, value in rw_graph.get(user_id, {}).items()]
        rw_top.sort(key=lambda x: -x[1])
        for item_id, _ in rw_top:
            if len(top) >= items_per_group:
                break
            if item_id in top or item_id in filter_items[user_id]:
                continue
            top.add(item_id)

        tail_top = book_top[poptop:]
        for item_id, _ in tail_top:
            if len(top) >= items_per_group:
                break
            if item_id in top or item_id in filter_items[user_id]:
                continue
            top.add(item_id)

        targets_found = len(top.intersection(target_items[user_id]))
        if targets_found == 0:
            bad_candidates_count += 1
            continue

        reduce_ts = user_last_ts if is_site_user(user_id) else start_ts
        top = list(sorted(top))
        for item_id in top:
            item = items[item_id]
            target = 1 if item_id in target_items[user_id] else 0
            features = calcer(user, item, reduce_ts)
            features = '\t'.join([str(ff) for ff in features])
            features_output.write('%s\t%s\t%d\t%s\n' % (user_id, item_id, target, features))
    features_output.close()
    print("Users with bad candidates: {}".format(bad_candidates_count))

    cd = calcer.get_cd()
    with open(os.path.join(input_directory, cd_output_path), "w") as cd_out:
        cd_out.write('0\tGroupId\tuser_id\n')
        cd_out.write('1\tAuxiliary\titem_id\n')
        cd_out.write('2\tLabel\ttarget\n')
        for i in range(len(cd.columns)):
            cd_out.write('%d\t%s\t%s\n' % (i+3, cd.columns[i][1], cd.columns[i][0]))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--input-directory', type=str, required=True)
    parser.add_argument('--item-profiles-path', type=str, required=True)
    parser.add_argument('--user-profiles-path', type=str, required=True)
    parser.add_argument('--profile-actions-path', type=str, required=True)
    parser.add_argument('--target-actions-path', type=str, required=True)
    parser.add_argument('--poptop', type=int, default=300)
    parser.add_argument('--items-per-group', type=int, default=600)
    parser.add_argument('--start-ts', type=int, required=True)
    parser.add_argument('--features-output-path', type=str, required=True)
    parser.add_argument('--cd-output-path', type=str, required=True)
    parser.add_argument('--rw-path', type=str, required=True)
    args = parser.parse_args()
    main(**vars(args))
