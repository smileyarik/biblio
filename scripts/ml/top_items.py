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
    output_path,
    start_ts,
):
    print("Read item profiles")
    items = dict()
    with open(os.path.join(input_directory, item_profiles_path), "r") as r:
        for line in tqdm(r):
            profile = Profile.loads(line)
            items[profile.object_id] = profile
    print("...{} items read".format(len(items)))

    print("Calc candidates")
    book_top = []
    for item_id, item in items.items():
        item_size = float(item.counters.get(OT.GLOBAL, CT.BOOKING, RT.D30, '', start_ts))
        book_top.append((item_id, item_size))
    book_top = sorted(book_top, key=lambda x: -x[1])
    with open(os.path.join(input_directory, output_path), "w") as out:
        for item_id, item_size in book_top[0:5]:
            out.write('0\t%d\t0\t%d\n' % (item_id, item_size))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--input-directory', type=str, required=True)
    parser.add_argument('--item-profiles-path', type=str, required=True)
    parser.add_argument('--output-path', type=str, required=True)
    parser.add_argument('--start-ts', type=int, required=True)
    args = parser.parse_args()
    main(**vars(args))
