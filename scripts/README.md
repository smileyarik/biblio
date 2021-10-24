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
