ver="001"

#cat ../src_data/circulaton_1.csv | head -1 > ../data/circulation.csv
#cat ../src_data/circulaton_* | iconv -f cp1251 -t utf8 | grep -v circulationID >> ../data/circulation.csv
#cat ../src_data/cat_1.csv | head -1 > ../data/cat.csv
#cat ../src_data/cat_* | iconv -f cp1251 -t utf8 | grep -v "recId;" >> ../data/cat.csv
#cat ../src_data/fund_1.csv | head -1 > ../data/fund.csv
#cat ../src_data/fund_* | iconv -f cp1251 -t utf8 | grep -v catalogueRecordID >> ../data/fund.csv
#cat ../src_data/readers.csv | iconv -f cp1251 -t utf8 > ../data/readers.csv
#cat ../src_data/bookpoints.csv | iconv -f cp1251 -t utf8 > ../data/bookpoints.csv
#cat ../src_data/rubrics.csv | iconv -f cp1251 -t utf8 > ../data/rubrics.csv
#cat ../src_data/series.csv | iconv -f cp1251 -t utf8 > ../data/series.csv
#cat ../src_data/persons.csv | iconv -f cp1251 -t utf8 > ../data/persons.csv
#cat ../src_data/authors.csv | iconv -f cp1251 -t utf8 > ../data/authors.csv

#python3 split.py ../data/circulation.csv ../data/minitr_st_circ.csv ../data/minitr_tg_circ.csv ../data/minivl_st_circ.csv ../data/minivl_tg_circ.csv ../data/minitt_st_circ.csv 01.10.2019 01.11.2019 01.11.2019 01.12.2019
#python3 split.py ../data/circulation.csv ../data/tr_st_circ.csv ../data/tr_tg_circ.csv ../data/vl_st_circ.csv ../data/vl_tg_circ.csv ../data/tt_st_circ.csv 01.07.2021 01.08.2021 01.08.2021 07.09.2021

#python3 make_profiles.py ../data/bookpoints.csv ../src_data/books.jsn ../data/readers.csv ../data/minitr_tg_circ.csv ../data/minitr_st_circ.csv ../data/minitr_user_pickle.bin ../data/minitr_item_pickle.bin
python3 make_profiles.py ../data/bookpoints.csv ../src_data/books.jsn ../data/readers.csv ../data/minivl_tg_circ.csv ../data/minivl_st_circ.csv ../data/minivl_user_pickle.bin ../data/minivl_item_pickle.bin
#python3 make_profiles.py ../data/bookpoints.csv ../src_data/books.jsn ../data/readers.csv ../data/tr_tg_circ.csv ../data/tr_st_circ.csv ../data/tr_user_pickle.bin ../data/tr_item_pickle.bin
#python3 make_profiles.py ../data/bookpoints.csv ../src_data/books.jsn ../data/readers.csv ../data/vl_tg_circ.csv ../data/vl_st_circ.csv ../data/vl_user_pickle.bin ../data/vl_item_pickle.bin

#python3 learn_rw.py 01.09.2019 ../data/minitr_tg_circ.csv ../data/minitr_st_circ.csv ../data/minitr_rw.bin
#python3 learn_rw.py 01.10.2019 ../data/minivl_tg_circ.csv ../data/minivl_st_circ.csv ../data/minivl_rw.bin
#python3 learn_rw.py 01.01.2021 ../data/tr_tg_circ.csv ../data/tr_st_circ.csv ../data/tr_rw.bin
#python3 learn_rw.py 01.02.2021 ../data/vl_tg_circ.csv ../data/vl_st_circ.csv ../data/vl_rw.bin


python3 make_features.py ../data/minitr_user_pickle.bin ../data/minitr_item_pickle.bin ../data/minitr_rw.bin 250 500 01.10.2019 ../data/minitr_tg_circ.csv ../data/minitr_features.txt ../data/minitr_cd.txt
python3 make_features.py ../data/minivl_user_pickle.bin ../data/minivl_item_pickle.bin ../data/minivl_rw.bin 250 500 01.11.2019 ../data/minivl_tg_circ.csv ../data/minivl_features.txt ../data/minivl_cd.txt
#python3 make_features.py ../data/tr_user_pickle.bin ../data/tr_item_pickle.bin ../data/tr_rw.bin 50 100 01.07.2021 ../data/tr_tg_circ.csv ../data/tr_features.txt ../data/tr_cd.txt
#python3 make_features.py ../data/vl_user_pickle.bin ../data/vl_item_pickle.bin ../data/vl_rw.bin 50 100 01.08.2021 ../data/vl_tg_circ.csv ../data/vl_features.txt ../data/vl_cd.txt


exit

cat ../data_new/tr_features.txt | awk -F '\t' -vOFS='\t' '{$1=$1"_tr";print $0}' > ../data_new/trall_features.txt
#cat ../data_new/tr2_features.txt | awk -F '\t' -vOFS='\t' '{$1=$1"_tr2";print $0}' >> ../data_new/trall_features.txt
#cat ../data_new/tr3_features.txt | awk -F '\t' -vOFS='\t' '{$1=$1"_tr3";print $0}' >> ../data_new/trall_features.txt

cat ../data_new/vl_features.txt | awk -F '\t' -vOFS='\t' '{$1=$1"_vl";print $0}' > ../data_new/trvl_features.txt
cat ../data_new/trall_features.txt  >> ../data_new/trvl_features.txt

# VANILLA
./catboost fit -f ../data_new/minitr_features.txt -t ../data_new/minivl_features.txt -m ../data_new/minitr_model.bin --cd ../data_new/minitr_cd.txt --loss-function YetiRank:decay=0.95 -i 500 --learn-err-log ../data_new/minitr_learn_error.txt --fstr-file ../data_new/minitr_model.fstr --fstr-type FeatureImportance --fstr-internal-file ../data_new/minitr_model.fstr_int --test-err-log ../data_new/minivl_learn_error.txt
./catboost fit -f ../data_new/tr_features.txt -t ../data_new/vl_features.txt -m ../data_new/tr_model.bin --cd ../data_new/tr_cd.txt --loss-function YetiRank:decay=0.95 -i 500 --learn-err-log ../data_new/tr_learn_error.txt --fstr-file ../data_new/tr_model.fstr --fstr-type FeatureImportance --fstr-internal-file ../data_new/tr_model.fstr_int --test-err-log ../data_new/vl_learn_error.txt

