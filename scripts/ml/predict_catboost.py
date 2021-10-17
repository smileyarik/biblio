import argparse
import os

from catboost import Pool, CatBoost


def main(
    input_directory,
    features_path,
    cd_path,
    model_path,
    output_path
):
    features_path = os.path.join(input_directory, features_path)
    cd_path = os.path.join(input_directory, cd_path)
    model_path = os.path.join(input_directory, model_path)

    user_ids = []
    item_ids = []
    with open(features_path) as r:
        for line in r:
            fields = line.strip().split()
            user_ids.append(fields[0])
            item_ids.append(fields[1])

    pool = Pool(data=features_path, column_description=cd_path)
    y_true = [int(l) for l in pool.get_label()]

    model= CatBoost()
    model.load_model(model_path)
    result = model.predict(pool)

    records = list(zip(user_ids, item_ids, y_true, result))
    records.sort(key=lambda x: (x[0], -x[3]))
    with open(os.path.join(input_directory, output_path), "w") as w:
        for record in records:
            w.write("{}\t{}\t{}\t{}\n".format(*record))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--input-directory', type=str, required=True)
    parser.add_argument('--features-path', type=str, default="valid_features.tsv")
    parser.add_argument('--cd-path', type=str, default="valid_cd.tsv")
    parser.add_argument('--model-path', type=str, required=True)
    parser.add_argument('--output-path', type=str, required=True)
    args = parser.parse_args()
    main(**vars(args))
