!/bin/bash

DIR="data_new"

TRAIN_START_TS=1569888000
TRAIN_FINISH_TS=1570060800
VALID_START_TS=1570060800
VALID_FINISH_TS=1570233600

mkdir -p $DIR

python3 -m ml.split \
    --input-directory $DIR \
    --actions-path actions.jsonl \
    --start-train-ts $TRAIN_START_TS \
    --finish-train-ts $TRAIN_FINISH_TS \
    --start-valid-ts $VALID_START_TS \
    --finish-valid-ts $VALID_FINISH_TS \
    --train-stat-path train_stat.jsonl \
    --train-target-path train_target.jsonl \
    --valid-stat-path valid_stat.jsonl \
    --valid-target-path valid_target.jsonl \
    --test-stat-path test_stat.jsonl

python3 -m ml.make_profiles \
    --input-directory $DIR \
    --profile-actions-path train_stat.jsonl \
    --target-actions-path train_target.jsonl \
    --item-profiles-path train_item_profiles.pkl \
    --user-profiles-path train_user_profiles.pkl \

python3 -m ml.make_profiles \
    --input-directory $DIR \
    --profile-actions-path valid_stat.jsonl \
    --target-actions-path valid_target.jsonl \
    --item-profiles-path valid_item_profiles.pkl \
    --user-profiles-path valid_user_profiles.pkl \

python3 -m ml.make_features \
    --input-directory $DIR \
    --profile-actions-path train_stat.jsonl \
    --target-actions-path train_target.jsonl \
    --item-profiles-path train_item_profiles.pkl \
    --user-profiles-path train_user_profiles.pkl \
    --start-ts $TRAIN_START_TS \
    --features-output-path train_features.tsv \
    --cd-output-path train_cd.tsv

python3 -m ml.make_features \
    --input-directory $DIR \
    --profile-actions-path valid_stat.jsonl \
    --target-actions-path valid_target.jsonl \
    --item-profiles-path valid_item_profiles.pkl \
    --user-profiles-path valid_user_profiles.pkl \
    --start-ts $VALID_START_TS \
    --features-output-path valid_features.tsv \
    --cd-output-path valid_cd.tsv

python3 -m ml.train_catboost.py \
    --input-directory $DIR  \
    --train-features-path train_features.tsv \
    --valid-features-path valid_features.tsv \
    --cd-path train_cd.tsv \
    --output-path model.bin
