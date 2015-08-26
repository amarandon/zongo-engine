runserver:
	../lib/google_appengine/dev_appserver.py .


dumpdb:
	python ../lib/google_appengine/bulkloader.py --dump --app_id=s~zongo-hrd --email=alex.marandon@gmail.com --url=http://www.zongosound.com/remote_api --filename=data.csv


restoredb:
	python ../lib/google_appengine/bulkloader.py --app_id=dev~zongo-hrd --batch_size=1 --restore --url=http://localhost:8080/remote_api --email=test@example.com --filename=data.csv
