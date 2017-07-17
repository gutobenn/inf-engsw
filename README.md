# engsw

### Installing
Setup virtualenv: ```virtualenv engsw```
Install dependencies: ```pip install -r requirements.txt``` (or pip3)

### Running
1. Activate virtualvenv: ```source ./bin/activate```

1. Both celery commands must run in separate terminals at same time:
	- Run celery-worker: ```celery -A engsw worker -l info```
	- Run celery-beat: ```celery -A engsw beat -l info```

1. Run server: ```python manage.py runserver``` (or python3)

[Access](http://127.0.0.1:8000)

[Trello](https://trello.com/b/RJKRXsxR/engsw)
