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

        

class EventForm(djangoforms.ModelForm):
    class Meta:
        model = Event
        exclude = ['atom_id']


class AdminPage(webapp.RequestHandler):

    def get(self):
        self.redirect("/admin/events")


class RequestHandler(webapp.RequestHandler):

    def render_to_response(self, template_filename, **kw):
        output = template.render('templates/' + template_filename, kw)
        self.response.out.write(output)


class ListEventHandler(RequestHandler):

    def get(self):
        self.render_to_response('admin/events_list.html', 
                    events=Event.get_reversed_list())


class NewEventHandler(RequestHandler):

    def get(self):
        self.render_to_response('admin/events_form.html', 
                form=EventForm(), operation='create')

    def post(self):
        data = EventForm(data=self.request.POST)
        if data.is_valid():
            event = data.save(commit=False)
            event.atom_id = event.build_atom_id()
            event.put()
            self.redirect("/admin/events")
        else:
            self.render_to_response('admin/events_form.html', form=data,
                    operation='create')


class EditEventHandler(RequestHandler):

    def get(self, id):
        event = Event.get_by_id(int(id))
        self.render_to_response('admin/events_form.html', 
                form=EventForm(instance=event), operation='update', id=id)

    def post(self, id):
        event = Event.get_by_id(int(id))
        assert event is not None
        data = EventForm(data=self.request.POST, instance=event)
        if data.is_valid():
            event = data.save(commit=False)
            event.put()
            self.redirect("/admin/events")
        else:
            self.render_to_response('admin/events_form.html', form=data,
                    operation='update', id=id)


class DeleteEventHandler(RequestHandler):

    def get(self, id):
        event = Event.get_by_id(int(id))
        db.delete(event)
        self.redirect("/admin/events")



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

def generate_admin_routes(name):
    prefix = '/admin/' + name + 's'
    map = { 
            '': 'List', 
            '/new': 'New', 
            '/create': 'New', 
            '/(\d+)/edit': 'Edit', 
            '/(\d+)/update': 'Edit', 
            '/(\d+)/delete': 'Delete'
            }
    routes = [(prefix + key, eval(value + name.capitalize() + 'Handler'))
            for key, value in map.items()]
    return routes



def main():
    logging.getLogger().setLevel(logging.DEBUG)
    routes = [ ('/', IndexPage), 
               ('/events/atom', EventsFeed), 
               ('/admin', AdminPage),
               ('/tests', TestPage) ]
    routes += generate_admin_routes('event')
    logging.debug(routes)
    application = webapp.WSGIApplication(routes, debug=True)
    wsgiref.handlers.CGIHandler().run(application)


if __name__ == "__main__":
    main()
