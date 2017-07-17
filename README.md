# engsw

### Installing
1. Setup virtualenv with python3: ```virtualenv -p python3  env```

2. Activate virtualvenv: ```source ./env/bin/activate```

3. Install dependencies: ```pip install -r requirements.txt```

### Running
1. Activate virtualvenv: ```source ./env/bin/activate```

1. Both celery commands must run in separate terminals at same time:
	- Run celery-worker: ```celery -A engsw worker -l info```
	- Run celery-beat: ```celery -A engsw beat -l info```

1. Run server: ```python manage.py runserver```

[Access](http://127.0.0.1:8000)

[Trello](https://trello.com/b/RJKRXsxR/engsw)
