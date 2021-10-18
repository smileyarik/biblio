### Download and refine data
```
bash +x download_data.sh ../../data
bash +x refine_data.sh ../../data ../../workdir
```

### Train model
```
bash +x run.sh ../../workdir
```

### Run tests
```
python -m unittest tests/test_profiles.py
```
