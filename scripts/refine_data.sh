#!/bin/bash

TEMP_DIR="temp"
OUTPUT_DIR="$1"

mkdir -p $TEMP_DIR
mkdir -p $OUTPUT_DIR

echo "-----downloads-----"
#cd $TEMP_DIR && wget https://www.dropbox.com/s/se6zn98ulv3ga0w/other_actions.tar.gz && tar -xzvf other_actions.tar.gz && cd ..
#cd $TEMP_DIR && wget https://www.dropbox.com/s/lgp8z4jhqacf91v/all_books.jsonl.tar.gz && tar -xzvf all_books.jsonl.tar.gz && cd ..
#cd $TEMP_DIR && wget https://www.dropbox.com/s/gl5z0s4q7h9kyll/actions.csv && cd ..
#cd $TEMP_DIR && wget https://www.dropbox.com/s/b2adss0k8n65stx/cat_3.csv && cd ..
#cd $TEMP_DIR && wget https://www.dropbox.com/s/nrositd7ceqid7p/circulaton_3.csv && cd ..
#cd $TEMP_DIR && wget https://www.dropbox.com/s/bm87xst2bn084t8/items.json && cd ..

echo "-----items-----"
python3 -m prepare.refine_items --input-directory $TEMP_DIR --output-path "$OUTPUT_DIR/items.jsonl"
echo "-----users-----"
python3 -m prepare.refine_users --input-directory $TEMP_DIR --output-path "$OUTPUT_DIR/users.jsonl"
echo "-----actions-----"
python3 -m prepare.refine_actions --input-directory $TEMP_DIR --output-path "$OUTPUT_DIR/actions.jsonl" --refined-items-path "$OUTPUT_DIR/items.jsonl" --refined-users-path "$OUTPUT_DIR/users.jsonl"

#rm -rf $TEMP_DIR
