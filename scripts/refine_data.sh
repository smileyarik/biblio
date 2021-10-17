#!/bin/bash

INPUT_DIR="$1"
OUTPUT_DIR="$2"

if [ ! -d "$INPUT_DIR" ]
then
    echo "Directory $INPUT_DIR DOES NOT exists."
    exit 1
fi

mkdir -p $OUTPUT_DIR

echo "-----items-----"
python3 -m prepare.refine_items --input-directory $INPUT_DIR --output-path "$OUTPUT_DIR/items.jsonl"

echo "-----users-----"
python3 -m prepare.refine_users --input-directory $INPUT_DIR --output-path "$OUTPUT_DIR/users.jsonl"

echo "-----actions-----"
python3 -m prepare.refine_actions --input-directory $INPUT_DIR --output-path "$OUTPUT_DIR/actions.jsonl" --refined-items-path "$OUTPUT_DIR/items.jsonl" --refined-users-path "$OUTPUT_DIR/users.jsonl"
