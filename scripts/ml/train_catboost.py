import argparse
import os
from catboost import Pool, CatBoost


def main(
    input_directory,
    train_features_path,
    valid_features_path,
    output_path,
    cd_path
):
    train_features_path = os.path.join(input_directory, train_features_path)
    valid_features_path = os.path.join(input_directory, valid_features_path)
    cd_path = os.path.join(input_directory, cd_path)
    output_path = os.path.join(input_directory, output_path)

    cb_model = CatBoost(params={
        "loss_function": "YetiRank:decay=0.95",
        "iterations": 500,
        "learning_rate": 0.05
    })
    train_pool = Pool(data=train_features_path, column_description=cd_path)
    valid_pool = Pool(data=valid_features_path, column_description=cd_path)
    cb_model.fit(train_pool, eval_set=valid_pool)
    cb_model.save_model(output_path)

    print(cb_model.get_feature_importance(valid_pool, prettified=True).head(10))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--input-directory', type=str, required=True)
    parser.add_argument('--train-features-path', type=str, default="train_features.tsv")
    parser.add_argument('--valid-features-path', type=str, default="valid_features.tsv")
    parser.add_argument('--output-path', type=str, required=True)
    parser.add_argument('--cd-path', type=str, default="train_cd.tsv")
    args = parser.parse_args()
    main(**vars(args))
