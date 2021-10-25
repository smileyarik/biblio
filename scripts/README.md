# Обучение
### Install requirements
```
pip install -r requirements.txt
```

### Download and refine data
```
bash +x download_data.sh ../../data
bash +x refine_data.sh ../../data ../../workdir
```

### Train model
```
bash +x train_model.sh ../../workdir
```

### Run tests
```
python -m unittest tests/test_profiles.py
```

# Применение
### Варка фикстур
```
bash +x make_recommendations.sh ../../workdir
```

### Заливка в админку
```
cd ../backend
python3 load_fixture.py ../../workdir/final_users_fixture.json
python3 load_fixture.py ../../workdir/final_items_fixture.json
python3 load_fixture.py ../../workdir/final_actions_fixture.json
python3 load_fixture.py ../../workdir/final_predictions_fixture.json
```

### Формирование сабмита (требует запещенного веб-сервера)
```
python3 make_submission.py --input-directory ../../data --recsys-host http://178.154.225.68:8000/ --output-path ../result_task3.csv
```
