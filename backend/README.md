### Install requirements
```
pip install -r requirements.txt
```

### Run recommender server
```
python manage.py migrate
python manage.py runserver 127.0.0.1:8000
```
Navigate to http://127.0.0.1:8000/recsys/api/predict?user_id=2
