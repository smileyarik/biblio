ver="001"

cat ../src_data/circulaton_1.csv | head -1 > ../data/circulation.csv
cat ../src_data/circulaton_* | iconv -f cp1251 -t utf8 | grep -v circulationID >> ../data/circulation.csv
cat ../src_data/cat_1.csv | head -1 > ../data/cat.csv
cat ../src_data/cat_* | iconv -f cp1251 -t utf8 | grep -v "recId;" >> ../data/cat.csv
cat ../src_data/fund_1.csv | head -1 > ../data/fund.csv
cat ../src_data/fund_* | iconv -f cp1251 -t utf8 | grep -v catalogueRecordID >> ../data/fund.csv
cat ../src_data/readers.csv | iconv -f cp1251 -t utf8 > ../data/readers.csv
cat ../src_data/bookpoints.csv | iconv -f cp1251 -t utf8 > ../data/bookpoints.csv
cat ../src_data/rubrics.csv | iconv -f cp1251 -t utf8 > ../data/rubrics.csv
cat ../src_data/series.csv | iconv -f cp1251 -t utf8 > ../data/series.csv
cat ../src_data/persons.csv | iconv -f cp1251 -t utf8 > ../data/persons.csv
cat ../src_data/authors.csv | iconv -f cp1251 -t utf8 > ../data/authors.csv

#python3 split.py ../data/circulation.csv ../data/minitr_st_circ.csv ../data/minitr_tg_circ.csv ../data/minivl_st_circ.csv ../data/minivl_tg_circ.csv ../data/minitt_st_circ.csv 01.10.2019 03.10.2019 03.10.2019 05.10.2019
python3 split.py ../data/circulation.csv ../data/tr_st_circ.csv ../data/tr_tg_circ.csv ../data/vl_st_circ.csv ../data/vl_tg_circ.csv ../data/tt_st_circ.csv 17.08.2021 24.08.2021 24.08.2021 31.08.2021

#python3 make_profiles.py ../data/bookpoints.csv ../src_data/books.jsn ../data/readers.csv ../data/minitr_tg_circ.csv ../data/minitr_st_circ.csv ../data/minitr_user_pickle.bin ../data/minitr_item_pickle.bin
#python3 make_profiles.py ../data/bookpoints.csv ../src_data/books.jsn ../data/readers.csv ../data/minivl_tg_circ.csv ../data/minivl_st_circ.csv ../data/minivl_user_pickle.bin ../data/minivl_item_pickle.bin
python3 make_profiles.py ../data/bookpoints.csv ../src_data/books.jsn ../data/readers.csv ../data/tr_tg_circ.csv ../data/tr_st_circ.csv ../data/tr_user_pickle.bin ../data/tr_item_pickle.bin
python3 make_profiles.py ../data/bookpoints.csv ../src_data/books.jsn ../data/readers.csv ../data/vl_tg_circ.csv ../data/vl_st_circ.csv ../data/vl_user_pickle.bin ../data/vl_item_pickle.bin

#python3 learn_rw.py 01.09.2019 ../data/minitr_tg_circ.csv ../data/minitr_st_circ.csv ../data/minitr_rw.bin
#python3 learn_rw.py 01.10.2019 ../data/minivl_tg_circ.csv ../data/minivl_st_circ.csv ../data/minivl_rw.bin
python3 learn_rw.py 17.02.2021 ../data/tr_tg_circ.csv ../data/tr_st_circ.csv ../data/tr_rw.bin
python3 learn_rw.py 24.02.2021 ../data/vl_tg_circ.csv ../data/vl_st_circ.csv ../data/vl_rw.bin


#python3 make_features.py ../data/minitr_user_pickle.bin ../data/minitr_item_pickle.bin ../data/minitr_rw.bin 50 100 01.10.2019 ../data/minitr_tg_circ.csv ../data/minitr_features.txt ../data/minitr_cd.txt ../data/minitr_st_circ.csv
#python3 make_features.py ../data/minivl_user_pickle.bin ../data/minivl_item_pickle.bin ../data/minivl_rw.bin 50 100 03.10.2019 ../data/minivl_tg_circ.csv ../data/minivl_features.txt ../data/minivl_cd.txt ../data/minivl_st_circ.csv
python3 make_features.py ../data/tr_user_pickle.bin ../data/tr_item_pickle.bin ../data/tr_rw.bin 100 200 17.07.2021 ../data/tr_tg_circ.csv ../data/tr_features.txt ../data/tr_cd.txt ../data/tr_st_circ.csv
python3 make_features.py ../data/vl_user_pickle.bin ../data/vl_item_pickle.bin ../data/vl_rw.bin 100 200 24.08.2021 ../data/vl_tg_circ.csv ../data/vl_features.txt ../data/vl_cd.txt ../data/vl_st_circ.csv

# VANILLA
#./catboost fit -f ../data/minitr_features.txt -t ../data/minivl_features.txt -m ../data/minitr_model.bin --cd ../data/minitr_cd.txt --loss-function YetiRank:decay=0.95 -i 500 --learn-err-log ../data/minitr_learn_error.txt --fstr-file ../data/minitr_model.fstr --fstr-type FeatureImportance --fstr-internal-file ../data/minitr_model.fstr_int --test-err-log ../data/minivl_learn_error.txt
./catboost fit -f ../data/tr_features.txt -t ../data/vl_features.txt -m ../data/tr_model.bin --cd ../data/tr_cd.txt --loss-function YetiRank:decay=0.95 -i 500 --learn-err-log ../data/tr_learn_error.txt --fstr-file ../data/tr_model.fstr --fstr-type FeatureImportance --fstr-internal-file ../data/tr_model.fstr_int --test-err-log ../data/vl_learn_error.txt

# calc metrics
./catboost calc -m ../data/tr_model.bin --cd ../data/tr_cd.txt -o ../data/vl_output.txt --input-path ../data/vl_features.txt
cat ../data/vl_output.txt | awk 'NR>1' > ../data/a_vl.txt;
cat ../data/vl_features.txt | awk -vOFS='\t' '{print $1,$2}' > ../data/b_vl.txt
paste ../data/b_vl.txt ../data/a_vl.txt > ../data/c_vl.txt
python3 make_result.py ../data/c_vl.txt 3 > ../data/answers_vl.txt

cat ../data/vl_features.txt | awk -vOFS='\t' '{print $1,$2,$4*1000000+$24}' > ../data/bb_vl.txt
paste ../data/bb_vl.txt ../data/a_vl.txt > ../data/cc_vl.txt
python make_result.py ../data/cc_vl.txt 2 > ../data/answers_pr_vl.txt

cat ../data/vl_features.txt | awk -vOFS='\t' '{print $1,$2,$24}' > ../data/bb_vl.txt
paste ../data/bb_vl.txt ../data/a_vl.txt > ../data/cc_vl.txt
python make_result.py ../data/cc_vl.txt 2 > ../data/answers_pop_vl.txt


echo "Catboost"
python3 split_answer.py ../data/vl_user_pickle.bin ../data/answers_vl.txt ../data/answers_vl_ ../data/vl_tg_circ.csv ../data/truth_vl_
for h in -1 0 1 2 3 4 5 6 7 8 9 10; do echo "= $h =";python3.9 score.py ../data/answers_vl_$h.txt ../data/truth_vl_$h.txt; done

echo "Pagerank"
python3 split_answer.py ../data/vl_user_pickle.bin ../data/answers_pr_vl.txt ../data/answers_pr_vl_ ../data/vl_tg_circ.csv ../data/truth_vl_
for h in -1 0 1 2 3 4 5 6 7 8 9 10; do echo "= $h =";python3.9 score.py ../data/answers_pr_vl_$h.txt ../data/truth_vl_$h.txt; done

echo "Item popularity"
python3 split_answer.py ../data/vl_user_pickle.bin ../data/answers_pop_vl.txt ../data/answers_pop_vl_ ../data/vl_tg_circ.csv ../data/truth_vl_
for h in -1 0 1 2 3 4 5 6 7 8 9 10; do echo "= $h =";python3.9 score.py ../data/answers_pop_vl_$h.txt ../data/truth_vl_$h.txt; done


