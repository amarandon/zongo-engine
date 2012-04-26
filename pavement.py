from paver.easy import *
import paver.doctools
from paver.setuputils import setup

@task
def dumpdb():
    print "Downloading data from App Engine"
    sh("python2.5 ../../lib/google_appengine/bulkloader.py --dump --app_id=zongo --email=alex.marandon@gmail.com --url=http://www.zongosound.com/remote_api --filename=data.csv")

@task
def restoredb():
    print "Loading data to development datastore."
    sh("python2.5 ../../lib/google_appengine/bulkloader.py --app_id=zongo --batch_size=1 --restore --url=http://localhost:8080/remote_api --email=admin --filename=data.csv")
