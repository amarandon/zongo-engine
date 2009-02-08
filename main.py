#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import os, sys

from UserList import UserList
import locale
from datetime import datetime
import wsgiref.handlers
import logging
log = logging.getLogger()
log.setLevel(logging.DEBUG)

from google.appengine.ext.webapp import util
from google.appengine.ext import webapp
from google.appengine.api import users
from google.appengine.ext import db

# Remove the standard version of Django.
for k in [k for k in sys.modules if k.startswith('django')]:
  del sys.modules[k]

# Force sys.path to have our own directory first, in case we want to import
# from it.
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))


# Must set this env var *before* importing any part of Django
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

from django.template.loader import render_to_string
from google.appengine.ext.db import djangoforms



DATE_FORMAT = '%d/%m/%Y'

class classproperty(object):
    def __init__(self, func):
        self.func = func

    def __get__(self, instance, owner):
        return self.func(owner)



class ZongoModel(db.Model):

    created_at = db.DateTimeProperty(auto_now_add=True)
    updated_at = db.DateTimeProperty(auto_now=True)
    atom_id = db.StringProperty()
    live = db.BooleanProperty(default=False, verbose_name="Publier")

    def __init__(self, parent=None, key_name=None, **kw):
        db.Model.__init__(self, parent=parent, key_name=key_name, **kw)
        self.atom_id = self.build_atom_id()

    @classproperty
    def admin_url(cls):
        name = cls.__name__.lower()
        url = '/admin/%ss' % name
        return url


    @classmethod
    def get_ordered_list(cls):
        if hasattr(cls, 'position'):
            order_criteria = 'position' 
        else:
            order_criteria = 'updated_at DESC'
        log.debug(order_criteria)
        return cls.gql("ORDER BY " + order_criteria)

    @property
    def id(self):
        return self.key().id()

    def build_atom_id(self):
        return "tag:%(domain_name)s,%(date)s:/%(collection_name)s/%(datetime)s" % dict(
                domain_name='zongosound.com',
                date=self.created_at.strftime("%Y-%m-%d"),
                datetime=self.created_at.strftime("%Y%m%d%H%M%S"),
                collection_name=self.code_name_plural
                )

    @property
    def formatted_live(self):
        return 'Oui' if self.live is True else 'Non'


class Link(ZongoModel):
    title = db.StringProperty(default=" ", 
            verbose_name='Titre')
    url = db.StringProperty(required=True)

    verbose_name = 'lien'
    verbose_name_plural = 'liens'

    code_name = 'link'
    code_name_plural = 'links'

    position = db.IntegerProperty(default=0)

    visible_properties = ('position', 'title', 'url', 'live')

    def __init__(self, parent=None, key_name=None, **kw):
        ZongoModel.__init__(self, parent=parent, key_name=key_name, **kw)


class Track(Link):

    verbose_name = 'morceau'
    verbose_name_plural = 'morceaux'

    code_name = 'track'
    code_name_plural = 'tracks'

    def __init__(self, parent=None, key_name=None, **kw):
        Link.__init__(self, parent=parent, key_name=key_name, **kw)

MOIS = ['Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin', 
        'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre']
JOURS = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi',
        'Dimanche']

class Event(ZongoModel):
    date = db.DateTimeProperty(required=True)
    location = db.StringProperty(required=True, verbose_name='Lieu')
    title = db.StringProperty(default=" ", 
            verbose_name='Intitulé (optionnel)')
    description = db.TextProperty(default=" ")
    image = db.BlobProperty()

    verbose_name = 'événement'
    verbose_name_plural = 'événements'

    code_name = 'event'
    code_name_plural = 'events'

    visible_properties = ('date', 'location', 'title', 'description', 'live')

    def __init__(self, parent=None, key_name=None, **kw):
        ZongoModel.__init__(self, parent=parent, key_name=key_name, **kw)

    @property
    def formatted_date(self):
        day = self.date.day
        if day == 1:
            day = '1er'
        month = MOIS[int(self.date.month) - 1]
        weekday = JOURS[self.date.weekday()]
        return "%s %s %s %s" % (weekday, day, month, self.date.year)

    @property
    def formatted_description(self):
        paragraphs = ["<p>%s</p>" % p for p in self.description_paragraphs] 
        return ''.join(paragraphs)

    @property
    def description_paragraphs(self):
        return self.description.split('\r\n\r\n')

    @property
    def short_description(self):
        return ' '.join(self.description.split()[:100]) + ' (...)'

    @property
    def url(self):
        return self.date.strftime("%Y/%m/%d") + '/' + str(self.id)

    def atom_updated_at(self):
        rfc3339date = self.updated_at.strftime("%Y-%m-%dT%H:%M:%S%z")
        return rfc3339date


    @classmethod
    def get_reversed_list(cls):
        return cls.gql("ORDER BY date DESC")

        



class RequestHandler(webapp.RequestHandler):

    def render_to_response(self, template_filename, **kw):
        output = render_to_string(template_filename, kw)
        self.response.out.write(output)

class AdminPage(RequestHandler):

    def get(self):
        self.render_to_response("admin/index.html", models=self.models)

class AdminListHandler(RequestHandler):

    def get(self):
        properties = self.model.properties()
        property_labels = [properties[name].verbose_name or name.capitalize() 
                                for name
                                in self.model.visible_properties]
        entities = self.model.get_ordered_list()

        entity_lists = []
        for entity in entities:
            entity_values = UserList()
            for property_name in self.model.visible_properties:
                if hasattr(entity, 'formatted_' + property_name):
                    entity_values.append(getattr(entity,  'formatted_' +
                        property_name))
                else:
                    entity_values.append(getattr(entity, property_name))
            entity_values.id = entity.id
            entity_lists.append(entity_values)

        self.render_to_response('admin/entity_list.html',
                    model=self.model,
                    entities=entity_lists,
                    property_labels=property_labels)


class AdminNewHandler(RequestHandler):

    def get(self):
        self.render_to_response('admin/entity_form.html', 
                form=self.form(), model=self.model, operation='create')

    def post(self):
        data = self.form(data=self.request.POST)
        if data.is_valid():
            entity = data.save(commit=False)
            for name, prop in self.model.properties().items():
                if isinstance(prop, db.BlobProperty):
                    if hasattr(self.request.POST[name], 'value'):
                        setattr(entity, name, self.request.POST[name].value)
            entity.put()
            self.redirect("/admin/%ss" % self.name)
        else:
            self.render_to_response('admin/entity_form.html', form=data, model=self.model, 
                    operation='create')


class AdminEditHandler(RequestHandler):

    def get(self, id):
        entity = self.model.get_by_id(int(id))
        self.render_to_response('admin/entity_form.html', 
                form=self.form(instance=entity), model=self.model, operation='update', id=id)

    def post(self, id):
        entity = self.model.get_by_id(int(id))
        assert entity is not None
        data = self.form(data=self.request.POST, instance=entity)
        if data.is_valid():
            entity = data.save(commit=False)
            for name, prop in self.model.properties().items():
                if isinstance(prop, db.BlobProperty):
                    if hasattr(self.request.POST[name], 'value'):
                        setattr(entity, name, self.request.POST[name].value)
            entity.put()
            self.redirect("/admin/%ss" % self.name)
        else:
            self.render_to_response('admin/entity_form.html', form=data, model=self.model,
                    operation='update', id=id)


class AdminDeleteHandler(RequestHandler):

    def get(self, id):
        entity = self.model.get_by_id(int(id))
        db.delete(entity)
        self.redirect("/admin/%ss" % self.name)



class IndexPage(RequestHandler):

    def get(self):
        self.render_to_response('index.html', 
                events=Event.get_reversed_list(),
                links=Link.get_ordered_list(),
                tracks=Track.get_ordered_list(),
                year=datetime.today().year
                )


class TestPage(webapp.RequestHandler):
    def get(self):
        locale.setlocale(locale.LC_ALL, 'fr_FR.UTF-8')
        d = datetime.strptime('12/12/1977', '%d/%m/%Y')
        s = d.strftime('%A %d %B %Y')
        self.response.out.write(s)

class EventImage(RequestHandler):
    def get(self, id):
        event = Event.get_by_id(int(id))
        if event.image:
            self.response.headers['Content-Type'] = "image/jpg"
            self.response.out.write(event.image)
        else:
            self.error(404)


class EventsFeed(RequestHandler):
    def get(self):
        event_list = Event.get_reversed_list()
        updated_at_list = [event.updated_at for event in event_list]
        latest_updated_at = max(updated_at_list)
        self.render_to_response('atom.xml', 
                events=event_list,
                host_url=self.request.host_url,
                updated_at=latest_updated_at
                )

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



def main():
    models = (Event, Track, Link)
    AdminPage.models = models
    routes = [ ('/', IndexPage), 
               ('/events/atom', EventsFeed), 
               ('/events/images/(\d+)', EventImage), 
               ('/admin', AdminPage),
               ('/tests', TestPage) ]
    for model in models:
        routes += admin_routes(model)
    application = webapp.WSGIApplication(routes, debug=True)
    util.run_wsgi_app(application)


if __name__ == "__main__":
    main()
