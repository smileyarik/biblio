#!/bin/bash

INPUT_DIR="../raw_data"
OUTPUT_DIR="../src_data"

cat $INPUT_DIR/circulaton_1.csv | head -1 > $OUTPUT_DIR/circulation.csv
cat $INPUT_DIR/circulaton_* | iconv -f cp1251 -t utf8 | grep -v circulationID >> $OUTPUT_DIR/circulation.csv
cat $INPUT_DIR/cat_1.csv | head -1 > $OUTPUT_DIR/cat.csv
cat $INPUT_DIR/cat_* | iconv -f cp1251 -t utf8 | grep -v "recId;" >> $OUTPUT_DIR/cat.csv
cat $INPUT_DIR/fund_1.csv | head -1 > $OUTPUT_DIR/fund.csv
cat $INPUT_DIR/fund_* | iconv -f cp1251 -t utf8 | grep -v catalogueRecordID >> $OUTPUT_DIR/fund.csv
cat $INPUT_DIR/readers.csv | iconv -f cp1251 -t utf8 > $OUTPUT_DIR/readers.csv
cat $INPUT_DIR/bookpoints.csv | iconv -f cp1251 -t utf8 > $OUTPUT_DIR/bookpoints.csv
cat $INPUT_DIR/rubrics.csv | iconv -f cp1251 -t utf8 > $OUTPUT_DIR/rubrics.csv
cat $INPUT_DIR/series.csv | iconv -f cp1251 -t utf8 > $OUTPUT_DIR/series.csv
cat $INPUT_DIR/persons.csv | iconv -f cp1251 -t utf8 > $OUTPUT_DIR/persons.csv
cat $INPUT_DIR/authors.csv | iconv -f cp1251 -t utf8 > $OUTPUT_DIR/authors.csv
