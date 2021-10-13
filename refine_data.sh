#!/bin/bash

INPUT_DIR="../src_data"
OUTPUT_DIR="../data1"

mkdir -p $OUTPUT_DIR

echo "-----books-----"
python3 scripts/refine_books.py --input-directory $INPUT_DIR --output-path "$OUTPUT_DIR/items.jsonl"
