import argparse
import requests
import os

from tqdm import tqdm
from util import read_csv


RECSYS_URL = '{}/recsys/api/predict?user_id={}&format=json'


def main(
    input_directory,
    site_actions_path,
    recsys_host,
    output_path
):
    site_actions = read_csv(os.path.join(input_directory, site_actions_path))
    user_ids = set(map(lambda a: int(a['user_id']), site_actions))
    user_ids.add(0) # user with no history
    print(f"{len(user_ids)} users")

    recommendations = dict()
    for user_id in tqdm(sorted(user_ids)):
        response = requests.get(RECSYS_URL.format(recsys_host.rstrip('/'), user_id))
        response.raise_for_status()

        recommendations[user_id] = [r['id'] for r in response.json()['recommendations']]

    with open(output_path, 'w') as f:
        f.write('user_id;book_id_1;book_id_2;book_id_3;book_id_4;book_id_5\n')
        for user_id, items in recommendations.items():
            f.write('{};{}\n'.format(user_id, ';'.join(map(str, items))))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--input-directory', type=str, required=True)
    parser.add_argument('--site-actions-path', type=str, default='actions.csv')
    parser.add_argument('--recsys-host', type=str, required=True)
    parser.add_argument('--output-path', type=str, required=True)
    args = parser.parse_args()
    main(**vars(args))
