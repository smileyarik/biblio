import argparse
import pickle
import os
from collections import defaultdict

from tqdm import tqdm

from ml.profiles import OT, CT, RT, Counters
from ml.features_lib import ColumnDescription, counter_cos
from util import read_jsonl


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
    with open(os.path.join(input_directory, user_profiles_path), "rb") as r:
        users = pickle.load(r)

    print("Read item profiles")
    with open(os.path.join(input_directory, item_profiles_path), "rb") as r:
        items = pickle.load(r)

    target_users = set()
    target_items = defaultdict(set)
    print("Read target users")
    target_actions = read_jsonl(os.path.join(input_directory, target_actions_path))
    for action in tqdm(target_actions):
        target_users.add(action["user_id"])
        target_items[action["user_id"]].add(action["item_uniq_id"])
    print("...{} target users".format(len(target_users)))

    filter_items = defaultdict(set)
    print("Read already seen items")
    stat_actions = read_jsonl(os.path.join(input_directory, profile_actions_path))
    for action in tqdm(stat_actions):
        filter_items[action["user_id"]].add(action["item_uniq_id"])

    print("Random walk load")
    rw_records = read_jsonl(os.path.join(input_directory, rw_path))
    rw_graph = defaultdict(lambda: defaultdict(float))
    for record in rw_records:
        rw_graph[record["user"]][record["item"]] = record["weight"]

    print("Calc candidates")
    book_top = []
    for item_id,item in items.items():
        item_size = float(item.get(OT.GLOBAL, CT.BOOKING, RT.D30, '', 0))
        book_top.append((item_id, item_size))
    book_top = sorted(book_top, key=lambda x:-x[1])

    print("Calc global stat")
    full_events = Counters()
    for item_id, item in items.items():
        for rt in [RT.SUM, RT.D7, RT.D30]:
            full_events.update_from(item, OT.GLOBAL, CT.BOOKING, rt, CT.BOOKING, rt, start_ts)

    print('All bookings 30d:', full_events.get(OT.GLOBAL, CT.BOOKING, RT.D30, '', start_ts))

    print("Calc features")
    ts = start_ts
    cd = ColumnDescription()
    features_output = open(os.path.join(input_directory, features_output_path), "w")
    for user_id in tqdm(target_users):
        user = users[user_id]
        top = book_top[:poptop]
        top_ids = {item_id for item_id, _ in top}

        rw_top = []
        for item_id, value in rw_graph.get(user_id, {}).items():
            rw_top.append((item_id, value))
        rw_top.sort(key=lambda x: -x[1])
        for item_id, rank in rw_top:
            if len(top) >= items_per_group:
                break
            if item_id in top_ids or item_id in filter_items[user_id]:
                continue
            top.append((item_id, rank))

        tail_top = book_top[poptop:]
        for item_id, rank in tail_top:
            if len(top) >= items_per_group:
                break
            if item_id in top_ids or item_id in filter_items[user_id]:
                continue
            top.append((item_id, rank))

        user_size = float(user.get(OT.GLOBAL, CT.BOOKING, RT.SUM, '', 0))
        found_target = 0
        for item_id, _ in top:
            if item_id in target_items[user_id]:
                found_target += 1
        if len(target_items[user_id]) > 0 and found_target == 0:
            continue

        for item_id, _ in top:
            item = items[item_id]
            target = 1 if item_id in target_items[user_id] else 0

            f = []
            f.append(rw_graph.get(user_id, {}).get(item_id, 0.0))
            cd.add('random_walk')

            for rt in [RT.SUM, RT.D7, RT.D30]:
                f.append(counter_cos(user, item, OT.AUTHOR, CT.BOOKING_BY, CT.HAS, rt, RT.SUM, ts))
                cd.add('author_cos_rt' + rt)
                f.append(counter_cos(user, item, OT.LIBRARY, CT.BOOKING, CT.BOOKING, rt, RT.SUM, ts))
                cd.add('library_cos_rt' + rt)
                f.append(counter_cos(user, item, OT.RUBRIC, CT.BOOKING_BY, CT.HAS, rt, RT.SUM, ts))
                cd.add('rubric_cos_rt' + rt)
                f.append(counter_cos(user, item, OT.SERIES, CT.BOOKING_BY, CT.HAS, rt, RT.SUM, ts))
                cd.add('series_cos_rt' + rt)

            for rt in [RT.SUM, RT.D7, RT.D30]:
                f.append(float(user.get(OT.GLOBAL, CT.BOOKING, rt, '', ts)))
                cd.add('user_size_rt' +  rt)

            for rt in [RT.SUM, RT.D7, RT.D30]:
                item_size = float(item.get(OT.GLOBAL, CT.BOOKING, rt, '', ts))
                full_size = float(full_events.get(OT.GLOBAL, CT.BOOKING, rt, '', ts))
                f.append(item_size / full_size)
                cd.add('item_size_rt' + rt)

            cd.finish()
            features = '\t'.join([str(ff) for ff in f])
            features_output.write('%s\t%s\t%d\t%s\n' % (user_id, item_id, target, features))

    features_output.close()
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
    parser.add_argument('--poptop', type=int, default=100)
    parser.add_argument('--items-per-group', type=int, default=200)
    parser.add_argument('--start-ts', type=int, required=True)
    parser.add_argument('--features-output-path', type=str, required=True)
    parser.add_argument('--cd-output-path', type=str, required=True)
    parser.add_argument('--rw-path', type=str, required=True)
    args = parser.parse_args()
    main(**vars(args))
