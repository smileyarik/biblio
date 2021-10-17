#!/bin/bash

OUTPUT_DIR="$1"

mkdir -p $OUTPUT_DIR

wget -c https://www.dropbox.com/s/se6zn98ulv3ga0w/other_actions.tar.gz -O - | tar -xzv -C $OUTPUT_DIR
wget -c https://www.dropbox.com/s/lgp8z4jhqacf91v/all_books.jsonl.tar.gz -O - | tar -xzv -C $OUTPUT_DIR
wget -P $OUTPUT_DIR https://www.dropbox.com/s/gl5z0s4q7h9kyll/actions.csv
wget -P $OUTPUT_DIR https://www.dropbox.com/s/b2adss0k8n65stx/cat_3.csv
wget -P $OUTPUT_DIR https://www.dropbox.com/s/nrositd7ceqid7p/circulaton_3.csv
wget -P $OUTPUT_DIR https://www.dropbox.com/s/bm87xst2bn084t8/items.json
