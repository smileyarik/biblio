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


#python make_profiles.py ../src_data_new/organisations.csv ../data_new/tr_st_reviews.csv ../src_data_new/users.csv ../src_data_new/aspects3.csv ../data_new/tr_tg_reviews.csv ../data_new/tr_user_pickle.bin ../data_new/tr_item_pickle.bin
#python make_profiles.py ../src_data_new/organisations.csv ../data_new/tr2_st_reviews.csv ../src_data_new/users.csv ../src_data_new/aspects3.csv ../data_new/tr2_tg_reviews.csv ../data_new/tr2_user_pickle.bin ../data_new/tr2_item_pickle.bin
#python make_profiles.py ../src_data_new/organisations.csv ../data_new/tr3_st_reviews.csv ../src_data_new/users.csv ../src_data_new/aspects3.csv ../data_new/tr3_tg_reviews.csv ../data_new/tr3_user_pickle.bin ../data_new/tr3_item_pickle.bin
#python make_profiles.py ../src_data_new/organisations.csv ../data_new/vl_st_reviews.csv ../src_data_new/users.csv ../src_data_new/aspects3.csv ../data_new/vl_tg_reviews.csv ../data_new/vl_user_pickle.bin ../data_new/vl_item_pickle.bin
#python make_profiles.py ../src_data_new/organisations.csv ../data_new/tt_st_reviews.csv ../src_data_new/users.csv ../src_data_new/aspects3.csv ../src_data_new/test_users.csv ../data_new/tt_user_pickle.bin ../data_new/tt_item_pickle.bin

#python learn_rw.py ../src_data_new/organisations.csv ../data_new/tr_st_reviews.csv ../src_data_new/users.csv ../data_new/tr_tg_reviews.csv ../data_new/tr_rw.bin
#python learn_rw.py ../src_data_new/organisations.csv ../data_new/tr2_st_reviews.csv ../src_data_new/users.csv ../data_new/tr2_tg_reviews.csv ../data_new/tr2_rw.bin
#python learn_rw.py ../src_data_new/organisations.csv ../data_new/tr3_st_reviews.csv ../src_data_new/users.csv ../data_new/tr3_tg_reviews.csv ../data_new/tr3_rw.bin
#python learn_rw.py ../src_data_new/organisations.csv ../data_new/vl_st_reviews.csv ../src_data_new/users.csv ../data_new/vl_tg_reviews.csv ../data_new/vl_rw.bin
#python learn_rw.py ../src_data_new/organisations.csv ../data_new/tt_st_reviews.csv ../src_data_new/users.csv ../src_data_new/test_users.csv ../data_new/tt_rw.bin

exit

#python make_features.py ../data_new/tr_user_pickle.bin ../data_new/tr_item_pickle.bin ../data_new/tr_tg_reviews.csv ../src_data_new/aspects3.csv ../src_data_new/rubrics.csv 1095 ../data_new/tr_features.txt ../data_new/cd.txt ../data_new/tr_rw.bin 0 1000
#python make_features.py ../data_new/tr2_user_pickle.bin ../data_new/tr2_item_pickle.bin ../data_new/tr2_tg_reviews.csv ../src_data_new/aspects3.csv ../src_data_new/rubrics.csv 485 ../data_new/tr2_features.txt ../data_new/cd.txt ../data_new/tr2_rw.bin 0 1000
#python make_features.py ../data_new/tr3_user_pickle.bin ../data_new/tr3_item_pickle.bin ../data_new/tr3_tg_reviews.csv ../src_data_new/aspects3.csv ../src_data_new/rubrics.csv 395 ../data_new/tr3_features.txt ../data_new/cd.txt ../data_new/tr3_rw.bin 0 1000
#python make_features.py ../data_new/vl_user_pickle.bin ../data_new/vl_item_pickle.bin ../data_new/vl_tg_reviews.csv ../src_data_new/aspects3.csv ../src_data_new/rubrics.csv 1185 ../data_new/vl_features.txt ../data_new/cd.txt ../data_new/vl_rw.bin 0 1000
#python make_features.py ../data_new/tt_user_pickle.bin ../data_new/tt_item_pickle.bin ../src_data_new/test_users.csv ../src_data_new/aspects3.csv ../src_data_new/rubrics.csv 1216 ../data_new/tt_features.txt ../data_new/cd.txt ../data_new/tt_rw.bin 0 1000

#cat ../data_new/tr_features.txt | awk -F '\t' -vOFS='\t' '{$1=$1"_tr";print $0}' > ../data_new/trall_features.txt
#cat ../data_new/tr2_features.txt | awk -F '\t' -vOFS='\t' '{$1=$1"_tr2";print $0}' >> ../data_new/trall_features.txt
#cat ../data_new/tr3_features.txt | awk -F '\t' -vOFS='\t' '{$1=$1"_tr3";print $0}' >> ../data_new/trall_features.txt

#cat ../data_new/vl_features.txt | awk -F '\t' -vOFS='\t' '{$1=$1"_vl";print $0}' > ../data_new/trvl_features.txt
#cat ../data_new/trall_features.txt  >> ../data_new/trvl_features.txt

# VANILLA
#./catboost fit -f ../data_new/tr_features.txt -t ../data_new/vl_features.txt -m ../data_new/tr_model.bin --cd ../data_new/cd.txt --loss-function YetiRank:decay=0.95 -i 500 --learn-err-log ../data_new/tr_learn_error.txt --fstr-file ../data_new/tr_model.fstr --fstr-type FeatureImportance --fstr-internal-file ../data_new/tr_model.fstr_int --test-err-log ../data_new/vl_learn_error.txt
#./catboost fit -f ../data_new/trall_features.txt -t ../data_new/vl_features.txt -m ../data_new/trall_model.bin --cd ../data_new/cd.txt --loss-function YetiRank:decay=0.95 -i 500 --learn-err-log ../data_new/trall_learn_error.txt --fstr-file ../data_new/trall_model.fstr --fstr-type FeatureImportance --fstr-internal-file ../data_new/trall_model.fstr_int --test-err-log ../data_new/vl_learn_error.txt
#./catboost fit -f ../data_new/tr3_features.txt -t ../data_new/vl_features.txt -m ../data_new/tr_model.bin --cd ../data_new/cd.txt --loss-function YetiRank:decay=0.95 -i 500 --learn-err-log ../data_new/tr_learn_error.txt --fstr-file ../data_new/tr_model.fstr --fstr-type FeatureImportance --fstr-internal-file ../data_new/tr_model.fstr_int --test-err-log ../data_new/vl_learn_error.txt

#./catboost fit -f ../data_new/trvl_features.txt -m ../data_new/trvl_model.bin --cd ../data_new/cd.txt --loss-function YetiRank -i 500 --learn-err-log ../data_new/trvl_learn_error.txt --fstr-file ../data_new/trvl_model.fstr --fstr-type FeatureImportance --fstr-internal-file ../data_new/trvl_model.fstr_int
#./catboost fit -f ../data_new/vl_features.txt -t ../data_new/tr2_features.txt -m ../data_new/trvl_model.bin --cd ../data_new/cd.txt --loss-function YetiRank:decay=0.95 -i 500 --learn-err-log ../data_new/trvl_learn_error.txt --fstr-file ../data_new/trvl_model.fstr --fstr-type FeatureImportance --fstr-internal-file ../data_new/trvl_model.fstr_int

# FEW FEATURES
#./catboost fit -f ../data_new/tr_features.txt -t ../data_new/vl_features.txt -m ../data_new/tr_model.bin --cd ../data_new/cd.txt --loss-function YetiRank:decay=0.95 -i 500 --learn-err-log ../data_new/tr_learn_error.txt --fstr-file ../data_new/tr_model.fstr --fstr-type FeatureImportance --fstr-internal-file ../data_new/tr_model.fstr_int --test-err-log ../data_new/vl_learn_error.txt -I 4:5-17:33-344
#./catboost fit -f ../data_new/trvl_features.txt -m ../data_new/trvl_model.bin --cd ../data_new/cd.txt --loss-function YetiRank:decay=0.95 -i 500 --learn-err-log ../data_new/trvl_learn_error.txt --fstr-file ../data_new/trvl_model.fstr --fstr-type FeatureImportance --fstr-internal-file ../data_new/trvl_model.fstr_int


# calc metrics
#./catboost calc -m ../data_new/tr_model.bin --cd ../data_new/cd.txt -o ../data_new/vl_output.txt --input-path ../data_new/vl_features.txt
#cat ../data_new/vl_output.txt | awk 'NR>1' > ../data_new/a_vl.txt;
#cat ../data_new/vl_features.txt | awk -vOFS='\t' '{print $1,$2}' > ../data_new/b_vl.txt
#paste ../data_new/b_vl.txt ../data_new/a_vl.txt > ../data_new/c_vl.txt
#python make_result.py ../data_new/c_vl.txt 3 > ../data_new/answers_vl.txt

#cat ../data_new/vl_features.txt | awk -vOFS='\t' '{print $1,$2,$5*1000000+$32}' > ../data_new/bb_vl.txt
#paste ../data_new/bb_vl.txt ../data_new/a_vl.txt > ../data_new/cc_vl.txt
#python make_result.py ../data_new/cc_vl.txt 2 > ../data_new/answers_pr_vl.txt

echo "Catboost"
python split_answer.py ../data_new/vl_user_pickle.bin ../data_new/answers_vl.txt ../data_new/answers_vl_ ../data_new/vl_tg_reviews.csv ../data_new/truth_vl_
for h in 0 1 2 3 4 5 6 7 8 9 10; do echo "= $h =";python score.py ../data_new/answers_vl_$h.txt ../data_new/truth_vl_$h.txt; done

#echo "Smart Pagerank"
#python split_answer.py ../data_new/vl_user_pickle.bin ../data_new/answers_pr_vl.txt ../data_new/answers_pr_vl_ ../data_new/vl_tg_reviews.csv ../data_new/truth_vl_
#for h in 0 1 2 3 4 5 6 7 8 9 10; do echo "= $h =";python score.py ../data_new/answers_pr_vl_$h.txt ../data_new/truth_vl_$h.txt; done

#for ff in $(jot 31 3); do
#    name=$(cat ../data_new/cd.txt | awk -vM=$ff '$1==M{print $3}');
#    echo $ff, $name
#    cat ../data_new/vl_features.txt | awk -vOFS='\t' -vM=$ff '{print $1,$2,$(M+1) + rand()*0.001}' > ../data_new/bb_vl.txt
#    paste ../data_new/bb_vl.txt ../data_new/a_vl.txt > ../data_new/cc_vl.txt
#    python make_result.py ../data_new/cc_vl.txt 2 > ../data_new/answers_f_vl.txt#

#    python split_answer.py ../data_new/vl_user_pickle.bin ../data_new/answers_f_vl.txt ../data_new/answers_f_vl_ ../data_new/vl_tg_reviews.csv ../data_new/truth_vl_
#    for h in 0 1 2 3 4 5 6 7 8 9 10; do echo "= $h =";python score.py ../data_new/answers_f_vl_$h.txt ../data_new/truth_vl_$h.txt; done
#done;

#exit

./catboost calc -m ../data_new/trvl_model.bin --cd ../data_new/cd.txt -o ../data_new/tt_output.txt --input-path ../data_new/tt_features.txt

cat ../data_new/tt_output.txt | awk 'NR>1' > ../data_new/a.txt;
cat ../data_new/tt_features.txt | awk -vOFS='\t' '{print $1,$2}' > ../data_new/b.txt
paste ../data_new/b.txt ../data_new/a.txt > ../data_new/c.txt

python make_result.py ../data_new/c.txt 3 > ../data_new/answers.txt


exit


python train_catboost.py ../data_new/vl_features_short_$ver.txt ../data_new/vl_features_short_$ver.txt ../data_new/model_$ver.cbm 400

#python train_catboost.py ../data_new/tr_features_$ver.txt ../data_new/vl_features_$ver.txt ../data_new/val_mmodel_$ver.cbm 1000
#python train_catboost_custom.py ../data_new/tr_features_$ver.txt ../data_new/vl_features_$ver.txt ../data_new/val_cmodel_$ver.cbm 100

./catboost calc -m ../data_new/model_$ver.cbm --cd cd -o ../data_new/tt_output_$ver.txt --input-path ../data_new/tt_features_$ver.txt --prediction-type Probability
#./catboost calc -m ../data_new/val_model_$ver.cbm --cd cd -o ../data_new/dbg_tt_output_$ver.txt --input-path ../data_new/tt_features_$ver.txt
#./catboost calc -m ../data_new/val_mmodel_$ver.cbm --cd cd -o ../data_new/vl_output_prob_$ver.txt --input-path ../data_new/vl_features_$ver.txt --prediction-type Probability
#./catboost calc -m ../data_new/val_mmodel_$ver.cbm --cd cd -o ../data_new/vl_output_$ver.txt --input-path ../data_new/vl_features_$ver.txt --prediction-type Probability

cat ../data_new/tt_output_$ver.txt | awk -vOFS=',' 'BEGIN{print "answer_id,score"}NR>1{v=-10*$2-0.1*$3+0.1*$4+0.5*$5;if(v>0){p=1}else{p=-1}print $1,p}' > ../data_new/result_$ver.csv


#cat ../data_new/tt_output_$ver.txt | awk -v OFS=',' 'BEGIN{print "answer_id,score"}NR>1{print $1,2./ (1 + exp(-$2)) - 1.}' > ../data_new/result_$ver.csv
#cat ../data_new/dbg_tt_output_$ver.txt | awk -v OFS=',' 'BEGIN{print "answer_id,score"}NR>1{print $1,2./ (1 + exp(-$2)) - 1.}' > ../data_new/dbg_result_$ver.csv
#cat ../data_new/vl_output_$ver.txt | awk -v OFS=',' 'NR>1{print $1,2./ (1 + exp(-$2)) - 1.}' > ../data_new/vl_result_$ver.csv
#cat ../data_new/dbg_vl_output_$ver.txt | awk -v OFS=',' 'NR>1{print $1,2./ (1 + exp(-$2)) - 1.}' > ../data_new/dbg_vl_result_$ver.csv

#cat ../data_new/vl_output_$ver.txt | awk -vOFS=',' 'BEGIN{print "answer_id,score"}NR>1{v=-10*$2-0.1*$3+0.1*$4+0.5*$5;if(v>0){p=1}else{p=-1}print $1,p}' > ../data_new/vl_result_$ver.csv

#catboost-gpu fit -f ../data_new/trvl_features_$ver.txt -m ../data_new/trvlmodel_$ver.bin --cd ../data_new/cd --loss-function YetiRank:decay=0.95 -i 4000 --learn-err-log ../data_new/trvllearn_error_$ver.txt --fstr-file ../data_new/trvlmodel_$ver.fstr --fstr-type FeatureImportance --fstr-internal-file ../data_new/trvlmodel_$ver.fstr_int --task-type GPU
#catboost-gpu calc -m ../data_new/trvlmodel_$ver.bin --cd ../data_new/cd -o ../data_new/tt_output_$ver.txt --input-path ../data_new/tt_features_$ver.txt 2> ../data_new/apply_stderr.txt

#cat ../data_new/tt_output_$ver.txt | awk 'NR>1' > ../data_new/a.txt;
#cat ../data_new/tt_features_$ver.txt | awk -vOFS='\t' '{print $1,$2}' > ../data_new/b.txt
#paste ../data_new/b.txt ../data_new/a.txt > ../data_new/c.txt

#python make_result.py ../data_new/c.txt 3 > ../data_new/result_trvl_$ver.json

