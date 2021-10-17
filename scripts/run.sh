#!/bin/bash

DIR="data_new"
FULL_TRAIN=1

if [ FULL_TRAIN == 1 ]; then
    TRAIN_PAGERANK_TS=1613520000
    VALID_PAGERANK_TS=1614124800
else
    TRAIN_PAGERANK_TS=1569542400
    VALID_PAGERANK_TS=1569888000
fi


mkdir -p $DIR

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

python3 -m ml.random_walk \
    --input-directory $DIR \
    --profile-actions-path train_stat.jsonl \
    --target-actions-path train_target.jsonl \
    --output-path train_random_walk.jsonl \
    --start-ts $TRAIN_PAGERANK_TS

python3 -m ml.random_walk \
    --input-directory $DIR \
    --profile-actions-path valid_stat.jsonl \
    --target-actions-path valid_target.jsonl \
    --output-path valid_random_walk.jsonl \
    --start-ts $VALID_PAGERANK_TS

python3 -m ml.make_features \
    --input-directory $DIR \
    --profile-actions-path train_stat.jsonl \
    --target-actions-path train_target.jsonl \
    --item-profiles-path train_item_profiles.pkl \
    --user-profiles-path train_user_profiles.pkl \
    --start-ts $TRAIN_START_TS \
    --features-output-path train_features.tsv \
    --cd-output-path train_cd.tsv \
    --rw-path train_random_walk.jsonl

python3 -m ml.make_features \
    --input-directory $DIR \
    --profile-actions-path valid_stat.jsonl \
    --target-actions-path valid_target.jsonl \
    --item-profiles-path valid_item_profiles.pkl \
    --user-profiles-path valid_user_profiles.pkl \
    --start-ts $VALID_START_TS \
    --features-output-path valid_features.tsv \
    --cd-output-path valid_cd.tsv \
    --rw-path valid_random_walk.jsonl

python3 -m ml.train_catboost \
    --input-directory $DIR  \
    --train-features-path train_features.tsv \
    --valid-features-path valid_features.tsv \
    --cd-path train_cd.tsv \
    --output-path model.bin

python3 -m ml.predict_catboost \
    --input-directory $DIR \
    --model-path model.bin \
    --output-path predictions.tsv

python3 -m ml.calc_score \
    --input-directory $DIR \
    --input-path predictions.tsv
