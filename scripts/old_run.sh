#!/bin/bash

FULL_TRAIN=0
INPUT_DIR="temp2"
TMP_DIR="temp3"

mkdir -p $TMP_DIR

if [ "$OSTYPE" == "darwin"* ]; then
    awk=gawk
fi

if [ FULL_TRAIN == 1 ]; then
    TRAIN_RW_START_DATE="17.02.2021" # 6 month for statistics till TRAIN_START_DATE
    TRAIN_START_DATE="17.08.2021"
    TRAIN_END_DATE="24.08.2021"
    VALID_RW_START_DATE="24.02.2021"
    VALID_START_DATE="24.08.2021"
    VALID_END_DATE="31.08.2021"
else
    TRAIN_RW_START_DATE="27.09.2019"
    TRAIN_START_DATE="01.10.2019"
    TRAIN_END_DATE="03.10.2019"
    VALID_RW_START_DATE="01.10.2019"
    VALID_START_DATE="03.10.2019"
    VALID_END_DATE="05.10.2019"
fi

echo ">>> $TRAIN_START_DATE..$TRAIN_END_DATE, $VALID_START_DATE..$VALID_END_DATE"

python3 -m ml.split $INPUT_DIR/circulation.csv $TMP_DIR/tr_st_circ.csv $TMP_DIR/tr_tg_circ.csv $TMP_DIR/vl_st_circ.csv $TMP_DIR/vl_tg_circ.csv $TMP_DIR/tt_st_circ.csv $TRAIN_START_DATE $TRAIN_END_DATE $VALID_START_DATE $VALID_END_DATE

python3 -m ml.make_profiles $INPUT_DIR/bookpoints.csv $INPUT_DIR/books.jsn $INPUT_DIR/readers.csv $TMP_DIR/tr_tg_circ.csv $TMP_DIR/tr_st_circ.csv $TMP_DIR/tr_user_pickle.bin $TMP_DIR/tr_item_pickle.bin
python3 -m ml.make_profiles $INPUT_DIR/bookpoints.csv $INPUT_DIR/books.jsn $INPUT_DIR/readers.csv $TMP_DIR/vl_tg_circ.csv $TMP_DIR/vl_st_circ.csv $TMP_DIR/vl_user_pickle.bin $TMP_DIR/vl_item_pickle.bin

python3 -m ml.learn_rw $TRAIN_RW_START_DATE $TMP_DIR/tr_tg_circ.csv $TMP_DIR/tr_st_circ.csv $TMP_DIR/tr_rw.bin
python3 -m ml.learn_rw $VALID_RW_START_DATE $TMP_DIR/vl_tg_circ.csv $TMP_DIR/vl_st_circ.csv $TMP_DIR/vl_rw.bin

python3 -m ml.make_features $TMP_DIR/tr_user_pickle.bin $TMP_DIR/tr_item_pickle.bin $TMP_DIR/tr_rw.bin 100 200 $TRAIN_START_DATE $TMP_DIR/tr_tg_circ.csv $TMP_DIR/tr_features.txt $TMP_DIR/tr_cd.txt $TMP_DIR/tr_st_circ.csv
python3 -m ml.make_features $TMP_DIR/vl_user_pickle.bin $TMP_DIR/vl_item_pickle.bin $TMP_DIR/vl_rw.bin 100 200 $VALID_START_DATE $TMP_DIR/vl_tg_circ.csv $TMP_DIR/vl_features.txt $TMP_DIR/vl_cd.txt $TMP_DIR/vl_st_circ.csv

# VANILLA
catboost fit -f $TMP_DIR/tr_features.txt -t $TMP_DIR/vl_features.txt -m $TMP_DIR/tr_model.bin --cd $TMP_DIR/tr_cd.txt --loss-function YetiRank:decay=0.95 -i 500 --learn-err-log $TMP_DIR/tr_learn_error.txt --fstr-file $TMP_DIR/tr_model.fstr --fstr-type FeatureImportance --fstr-internal-file $TMP_DIR/tr_model.fstr_int --test-err-log $TMP_DIR/vl_learn_error.txt

# calc metrics
catboost calc -m $TMP_DIR/tr_model.bin --cd $TMP_DIR/tr_cd.txt -o $TMP_DIR/vl_output.txt --input-path $TMP_DIR/vl_features.txt


cat $TMP_DIR/vl_output.txt | awk 'NR>1' > $TMP_DIR/a_vl.txt;
cat $TMP_DIR/vl_features.txt | awk -vOFS='\t' '{print $1,$2}' > $TMP_DIR/b_vl.txt
paste $TMP_DIR/b_vl.txt $TMP_DIR/a_vl.txt > $TMP_DIR/c_vl.txt
python3 -m ml.make_result $TMP_DIR/c_vl.txt 3 > $TMP_DIR/answers_vl.txt

cat $TMP_DIR/vl_features.txt | awk -vOFS='\t' '{print $1,$2,$4*1000000+$24}' > $TMP_DIR/bb_vl.txt
paste $TMP_DIR/bb_vl.txt $TMP_DIR/a_vl.txt > $TMP_DIR/cc_vl.txt
python3 -m ml.make_result $TMP_DIR/cc_vl.txt 2 > $TMP_DIR/answers_pr_vl.txt

cat $TMP_DIR/vl_features.txt | awk -vOFS='\t' '{print $1,$2,$24}' > $TMP_DIR/bb_vl.txt
paste $TMP_DIR/bb_vl.txt $TMP_DIR/a_vl.txt > $TMP_DIR/cc_vl.txt
python3 -m ml.make_result $TMP_DIR/cc_vl.txt 2 > $TMP_DIR/answers_pop_vl.txt


echo "Catboost"
python3 -m ml.split_answer $TMP_DIR/vl_user_pickle.bin $TMP_DIR/answers_vl.txt $TMP_DIR/answers_vl_ $TMP_DIR/vl_tg_circ.csv $TMP_DIR/truth_vl_
for h in -1 0 1 2 3 4 5 6 7 8 9 10; do echo "= $h =";python3 -m ml.score $TMP_DIR/answers_vl_$h.txt $TMP_DIR/truth_vl_$h.txt; done

echo "Pagerank"
python3 -m ml.split_answer $TMP_DIR/vl_user_pickle.bin $TMP_DIR/answers_pr_vl.txt $TMP_DIR/answers_pr_vl_ $TMP_DIR/vl_tg_circ.csv $TMP_DIR/truth_vl_
for h in -1 0 1 2 3 4 5 6 7 8 9 10; do echo "= $h =";python3 -m ml.score $TMP_DIR/answers_pr_vl_$h.txt $TMP_DIR/truth_vl_$h.txt; done

echo "Item popularity"
python3 -m ml.split_answer $TMP_DIR/vl_user_pickle.bin $TMP_DIR/answers_pop_vl.txt $TMP_DIR/answers_pop_vl_ $TMP_DIR/vl_tg_circ.csv $TMP_DIR/truth_vl_
for h in -1 0 1 2 3 4 5 6 7 8 9 10; do echo "= $h =";python3 -m ml.score $TMP_DIR/answers_pop_vl_$h.txt $TMP_DIR/truth_vl_$h.txt; done
