import os, sys

from paver.easy import *
import paver.doctools
from paver.setuputils import setup

gaepath = os.environ.get("GAEPATH")
if not gaepath:
    sys.abort("Please set the GAEPATH environment variable to the path of the Google App Engine SDK.")
sys.path.append(os.path.join(gaepath, 'lib', 'yaml', 'lib'))
sys.path.append(os.path.join(gaepath, 'lib', 'antlr3'))
sys.path.append(os.path.join(gaepath, 'lib', 'ipaddr'))

from google.appengine.tools import appcfg

@task
def startserver():
    sh("%s/dev_appserver.py ." % gaepath)

@task
def dumpdb():
    print "Downloading data from App Engine"
    sh("%s/bulkloader.py --dump --app_id=zongo --email=alex.marandon@gmail.com --url=http://www.zongosound.com/remote_api --filename=data.csv" % gaepath)

@task
def restoredb():
    print "Loading data to development datastore."
    args = "appcfg.py upload_data -A zongo --batch_size=1 --url=http://localhost:8080/remote_api --email=admin --filename=data.csv"
    argv = args.split()
    appcfg.main(argv)
