#!/bin/bash

DIR="$1"
RECOMMENDER_TS=1630962000 # 7 сентября 2021 г., 0:00:00 GMT+03:00

if [ ! -d "$DIR" ]
then
    echo "Directory $DIR DOES NOT exists."
    exit 1
fi

echo "==== Filter actions (all)"
python3 -m ml.filter_actions \
    --input-directory $DIR \
    --actions-path actions.jsonl \
    --new-actions-path filter_actions.jsonl

echo "==== Make profiles"
python3 -m ml.make_profiles \
    --input-directory $DIR \
    --profile-actions-path filter_actions.jsonl \
    --make-for-site \
    --item-profiles-path final_item_profiles.jsonl \
    --user-profiles-path final_user_profiles.jsonl

echo "==== Filter actions (site)"
python3 -m ml.filter_actions \
    --input-directory $DIR \
    --actions-path actions.jsonl \
    --new-actions-path site_actions.jsonl \
    --site

# TODO: add random_walk trained on full data

echo "==== Make features"
python3 -m ml.make_features \
    --input-directory $DIR \
    --profile-actions-path site_actions.jsonl \
    --item-profiles-path final_item_profiles.jsonl \
    --user-profiles-path final_user_profiles.jsonl \
    --start-ts $RECOMMENDER_TS \
    --features-output-path final_features.tsv \
    --cd-output-path final_cd.tsv \
    --rw-path valid_random_walk.jsonl \
    --rw-top-size 200 \
    --items-per-group 600

echo "==== Predict catboost"
python3 -m ml.predict_catboost \
    --input-directory $DIR \
    --features-path final_features.tsv
    --cd-path final_cd.tsv
    --model-path model.bin \
    --output-path final_predictions.tsv

echo "==== Make items fixture"
python3 -m deploy.make_items_fixture \
    --input-directory $DIR \
    --items-path items.jsonl \
    --fixture-path final_items_fixture.json

echo "==== Make users fixture"
python3 -m deploy.make_users_fixture \
    --input-directory $DIR \
    --actions-path site_actions.jsonl \
    --fixture-path final_users_fixture.json

echo "==== Make actions fixture"
python3 -m deploy.make_actions_fixture \
    --input-directory $DIR \
    --actions-path site_actions.jsonl \
    --fixture-path final_actions_fixture.json

echo "==== Make predictions fixture"
python3 -m deploy.make_predictions_fixture \
    --input-directory $DIR \
    --predictions-path final_predictions.tsv \
    --fixture-path final_predictions_fixture.json
