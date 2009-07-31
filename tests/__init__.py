import unittest
from datetime import datetime

from webtest import TestApp

from google.appengine.api import apiproxy_stub_map
from google.appengine.api import datastore_file_stub

from main import application

def clear_datastore():

    apiproxy_stub_map.apiproxy = apiproxy_stub_map.APIProxyStubMap()
    stub = datastore_file_stub.DatastoreFileStub('zongo', '/dev/null',
               '/dev/null')
    apiproxy_stub_map.apiproxy.RegisterStub('datastore_v3', stub)


class BaseTest(unittest.TestCase):

    @staticmethod
    def str2date(s):
        return datetime.strptime(s, "%Y-%m-%d")


    def setUp(self):
        clear_datastore()
        self.app = TestApp(application())
