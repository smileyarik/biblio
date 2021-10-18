#!/bin/bash

DIR="$1"
FULL_TRAIN=1

if [ $FULL_TRAIN == 1 ]; then
    TRAIN_PAGERANK_TS=1613520000
    TRAIN_START_TS=1629158400
    TRAIN_FINISH_TS=1629763200
    VALID_PAGERANK_TS=1614124800
    VALID_START_TS=1629763200
    VALID_FINISH_TS=1630368000
else
    TRAIN_PAGERANK_TS=1569542400
    TRAIN_START_TS=1569888000
    TRAIN_FINISH_TS=1570060800
    VALID_PAGERANK_TS=1569888000
    VALID_START_TS=1570060800
    VALID_FINISH_TS=1570233600
fi

if [ ! -d "$DIR" ]
then
    echo "Directory $DIR DOES NOT exists."
    exit 1
fi

echo "==== Split actions"
python3 -m ml.split_actions \
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

echo "==== Make profiles (train)"
python3 -m ml.make_profiles \
    --input-directory $DIR \
    --profile-actions-path train_stat.jsonl \
    --target-actions-path train_target.jsonl \
    --item-profiles-path train_item_profiles.jsonl \
    --user-profiles-path train_user_profiles.jsonl

echo "==== Make profiles (valid)"
python3 -m ml.make_profiles \
    --input-directory $DIR \
    --profile-actions-path valid_stat.jsonl \
    --target-actions-path valid_target.jsonl \
    --item-profiles-path valid_item_profiles.jsonl \
    --user-profiles-path valid_user_profiles.jsonl

echo "==== Random walk (train)"
python3 -m ml.random_walk \
    --input-directory $DIR \
    --profile-actions-path train_stat.jsonl \
    --target-actions-path train_target.jsonl \
    --output-path train_random_walk.jsonl \
    --start-ts $TRAIN_PAGERANK_TS \
    --probability 0.1

echo "==== Random walk (valid)"
python3 -m ml.random_walk \
    --input-directory $DIR \
    --profile-actions-path valid_stat.jsonl \
    --target-actions-path valid_target.jsonl \
    --output-path valid_random_walk.jsonl \
    --start-ts $VALID_PAGERANK_TS \
    --probability 0.1

echo "==== Make features (train)"
python3 -m ml.make_features \
    --input-directory $DIR \
    --profile-actions-path train_stat.jsonl \
    --target-actions-path train_target.jsonl \
    --item-profiles-path train_item_profiles.jsonl \
    --user-profiles-path train_user_profiles.jsonl \
    --start-ts $TRAIN_START_TS \
    --features-output-path train_features.tsv \
    --cd-output-path train_cd.tsv \
    --rw-path train_random_walk.jsonl

echo "==== Make features (valid)"
python3 -m ml.make_features \
    --input-directory $DIR \
    --profile-actions-path valid_stat.jsonl \
    --target-actions-path valid_target.jsonl \
    --item-profiles-path valid_item_profiles.jsonl \
    --user-profiles-path valid_user_profiles.jsonl \
    --start-ts $VALID_START_TS \
    --features-output-path valid_features.tsv \
    --cd-output-path valid_cd.tsv \
    --rw-path valid_random_walk.jsonl

echo "==== Train catboost"
python3 -m ml.train_catboost \
    --input-directory $DIR  \
    --train-features-path train_features.tsv \
    --valid-features-path valid_features.tsv \
    --cd-path train_cd.tsv \
    --output-path model.bin

echo "==== Predict catboost"
python3 -m ml.predict_catboost \
    --input-directory $DIR \
    --model-path model.bin \
    --output-path predictions.tsv

echo "==== Calc score"
python3 -m ml.calc_score \
    --input-directory $DIR \
    --input-path predictions.tsv
