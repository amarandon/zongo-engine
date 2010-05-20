#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import os, sys

import wsgiref.handlers
import logging
log = logging.getLogger()
log.setLevel(logging.DEBUG)

from google.appengine.ext.webapp import util
from google.appengine.ext import webapp

# Remove the standard version of Django.
for k in [k for k in sys.modules if k.startswith('django')]:
  del sys.modules[k]

# Force sys.path to have our own directory first, in case we want to import
# from it.
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Must set this env var *before* importing any part of Django
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

from google.appengine.ext.db import djangoforms
from public_handlers import *
from admin_handlers import *

def admin_routes(Model):
    map = { 
            '': 'List', 
            '/new': 'New', 
            '/create': 'New', 
            '/(\d+)/edit': 'Edit', 
            '/(\d+)/update': 'Edit', 
            '/(\d+)/delete': 'Delete'
            }
    name = Model.__name__.lower()
    prefix = Model.admin_url

    class Form(djangoforms.ModelForm):
        class Meta:
            model = Model
            exclude = ['atom_id']

    routes = [(prefix + path, type(action + name + 'Handler',
                                   (globals()['Admin' + action + 'Handler'],), 
                                   dict(model=Model, name=name, form=Form)))
                        for path, action in map.items()]
    return routes


def application():
    models = (Event, Track, Link, Image)
    AdminPage.models = models
    routes = [ ('/', IndexPage), 
               ('/events/atom', EventsFeed), 
               ('/events/images/(\d+)', EventImage), 
               ('/events/images/(\d+).jpg', EventImage), 
               ('/events/images/Flyer-Zongo-Sound-([^/]+).jpg', EventImageFromSlug), 
               ('/events/small_images/(\d+).jpg', EventSmallImage), 
               ('/events/([^/]+)/?', EventPage), 
               ('/photos/?', PhotoGalleryHandler), 
               ('/photos/([^/]+)/.+', PhotoHandler), 
               ('/thumbnail/([^/]+)/.+', ThumbnailHandler), 
               ('/admin', AdminPage),
               ('/tests', TestPage) ]
    for model in models:
        routes += admin_routes(model)
    return webapp.WSGIApplication(routes, debug=True)

def main():
    util.run_wsgi_app(application())


if __name__ == "__main__":
    main()
