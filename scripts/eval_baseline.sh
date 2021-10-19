#!/bin/bash

DIR="$1"
BASELINE="$2" # popular, random_walk, random

TEMP_FILE="_baseline_predictions.tsv"

echo "==== Calc baseline"
python3 -m ml.predict_baseline \
    --input-directory $DIR \
    --profile-actions-path valid_stat.jsonl \
    --target-actions-path valid_target.jsonl \
    --item-profiles-path valid_item_profiles.jsonl \
    --user-profiles-path valid_user_profiles.jsonl \
    --rw-path valid_random_walk.jsonl \
    --output-path baseline_random.tsv \
    --baseline-name $BASELINE \
    --output-path $TEMP_FILE

echo "==== Calc score"
python3 -m ml.calc_score \
    --input-directory $DIR \
    --input-path $TEMP_FILE

rm $TEMP_FILE
