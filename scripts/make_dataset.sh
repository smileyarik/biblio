!/bin/bash

INPUT_DIR="$1"
OUTPUT_DIR="$2"

FULL_TRAIN=1

if [ ! -d "$INPUT_DIR" ]
then
    echo "Directory $INPUT_DIR DOES NOT exists."
    exit 1
fi

mkdir -p $OUTPUT_DIR

if [ FULL_TRAIN == 1 ]; then
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

python3 -m ml.split_actions \
    --input-directory $INPUT_DIR \
    --output-directory $OUTPUT_DIR \
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
