#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from datetime import datetime
import locale
import cgi
from datetime import datetime
import wsgiref.handlers
import logging

from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext import db

from google.appengine.ext.db import djangoforms

DATE_FORMAT = '%d/%m/%Y'

class Event(db.Model):
    date = db.DateTimeProperty(required=True)
    location = db.StringProperty(required=True, verbose_name='Lieu')
    title = db.StringProperty(default=" ", 
            verbose_name='Intitulé (optionnel)')
    description = db.TextProperty(default=" ")
    live = db.BooleanProperty(default=False, verbose_name="Publier")
    created_at = db.DateTimeProperty(auto_now_add=True)
    updated_at = db.DateTimeProperty(auto_now=True)
    atom_id = db.StringProperty()

    verbose_name = 'événement'
    verbose_name_plural = 'événements'

    code_name = 'event'
    code_name_plural = 'events'

    visible_properties = ('date', 'location', 'title', 'description', 'live')

    def __init__(self, parent=None, key_name=None, **kw):
        db.Model.__init__(self, parent=parent, key_name=key_name, **kw)
        self.atom_id = self.build_atom_id()

    @property
    def formatted_date(self):
        return self.date.strftime(DATE_FORMAT)

    @property
    def description_paragraphs(self):
        return self.description.split('\r\n\r\n')

    @property
    def short_description(self):
        return ' '.join(self.description.split()[:100]) + ' (...)'

    @property
    def formatted_live(self):
        return 'Oui' if self.live is True else 'Non'

    @property
    def url(self):
        return self.date.strftime("%Y/%m/%d") + '/' + str(self.id)

    @property
    def id(self):
        return self.key().id()

    def build_atom_id(self):
        return "tag:%(domain_name)s,%(date)s:/events/%(datetime)s" % dict(
                domain_name='zongosound.com',
                date=self.created_at.strftime("%Y-%m-%d"),
                datetime=self.created_at.strftime("%Y%m%d%H%M%S")
                )

    def atom_updated_at(self):
        rfc3339date = self.updated_at.strftime("%Y-%m-%dT%H:%M:%S%z")
        return rfc3339date


    @classmethod
    def get_reversed_list(cls):
        return cls.gql("ORDER BY date DESC")

        

class AdminPage(webapp.RequestHandler):

    def get(self):
        self.redirect("/admin/events")


class RequestHandler(webapp.RequestHandler):

    def render_to_response(self, template_filename, **kw):
        output = template.render('templates/' + template_filename, kw)
        self.response.out.write(output)


class AdminListHandler(RequestHandler):

    def get(self):
        properties = self.model.properties()
        property_labels = [properties[name].verbose_name or name.capitalize() 
                                for name
                                in self.model.visible_properties]
        self.render_to_response('admin/%ss_list.html' % self.name, 
                    entities=self.model.get_reversed_list(),
                    property_labels=property_labels)


class AdminNewHandler(RequestHandler):

    def get(self):
        self.render_to_response('admin/%ss_form.html' % self.name, 
                form=self.form(), model=self.model, operation='create')

    def post(self):
        data = self.form(data=self.request.POST)
        if data.is_valid():
            entity = data.save(commit=False)
            entity.put()
            self.redirect("/admin/%ss" % self.name)
        else:
            self.render_to_response('admin/%ss_form.html' % self.name, form=data, model=self.model, 
                    operation='create')


class AdminEditHandler(RequestHandler):

    def get(self, id):
        entity = self.model.get_by_id(int(id))
        self.render_to_response('admin/%ss_form.html' % self.name, 
                form=self.form(instance=entity), model=self.model, operation='update', id=id)

    def post(self, id):
        entity = self.model.get_by_id(int(id))
        assert entity is not None
        data = self.form(data=self.request.POST, instance=entity)
        if data.is_valid():
            entity = data.save(commit=False)
            entity.put()
            self.redirect("/admin/%ss" % self.name)
        else:
            self.render_to_response('admin/%ss_form.html' % self.name, form=data, model=self.model,
                    operation='update', id=id)


class AdminDeleteHandler(RequestHandler):

    def get(self, id):
        entity = self.model.get_by_id(int(id))
        db.delete(entity)
        self.redirect("/admin/%ss" % self.name)



class IndexPage(RequestHandler):

    def get(self):
        self.render_to_response('index.html', 
                events=Event.get_reversed_list())


class TestPage(webapp.RequestHandler):
    def get(self):
        locale.setlocale(locale.LC_ALL, 'fr_FR.UTF-8')
        d = datetime.strptime('12/12/1977', '%d/%m/%Y')
        s = d.strftime('%A %d %B %Y')
        self.response.out.write(s)


class EventsFeed(RequestHandler):
    def get(self):
        self.render_to_response('atom.xml', 
                events=Event.get_reversed_list(),
                host_url=self.request.host_url)

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
    prefix = '/admin/%ss' % name

    class Form(djangoforms.ModelForm):
        class Meta:
            model = Model
            exclude = ['atom_id']

    routes = [(prefix + path, type(action + name + 'Handler',
                                   (eval('Admin' + action + 'Handler'),), 
                                   dict(model=Model, name=name, form=Form)))
                        for path, action in map.items()]
    return routes



def main():
    logging.getLogger().setLevel(logging.DEBUG)
    routes = [ ('/', IndexPage), 
               ('/events/atom', EventsFeed), 
               ('/admin', AdminPage),
               ('/tests', TestPage) ]
    routes += admin_routes(Event)
    logging.debug(routes)
    application = webapp.WSGIApplication(routes, debug=True)
    wsgiref.handlers.CGIHandler().run(application)


if __name__ == "__main__":
    main()
