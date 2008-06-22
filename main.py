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
    title = db.StringProperty(default=" ", verbose_name='Intitulé (optionnel)')
    description = db.TextProperty(default=" ")

    @property
    def formatted_date(self):
        return self.date.strftime(DATE_FORMAT)

    @property
    def id(self):
        return self.key().id()

    @classmethod
    def get_reversed_list(cls):
        return cls.gql("ORDER BY date DESC")
        

class EventForm(djangoforms.ModelForm):
    class Meta:
        model = Event


class AdminPage(webapp.RequestHandler):

    def get(self):
        self.redirect("/admin/events")


class EventsDeleteHandler(webapp.RequestHandler):

    def get(self):
        id = self.request.get('id')
        event = Event.get(db.Key.from_path('Event', int(id)))
        db.delete(event)
        self.redirect("/admin/events")


class EventsManager(webapp.RequestHandler):

    def get(self):
        template_params = dict(events=Event.get_reversed_list())
        id = self.request.get('id')
        if id:
            event = Event.get(db.Key.from_path('Event', int(id)))
            template_params['form'] = EventForm(instance=event)
            template_params['operation'] = 'update'
            template_params['id'] = id
        else:
            template_params['form'] = EventForm()
            template_params['operation'] = 'create'
        self.response.out.write(
                template.render('templates/events_manager.html', 
                    template_params))

    def post(self):
        operation="create"
        if self.request.get('create'):
            data = EventForm(data=self.request.POST)
        elif self.request.get('update'):
            operation="update"
            id = int(self.request.get('id'))
            event = Event.get(db.Key.from_path('Event', id))
            assert event is not None
            data = EventForm(data=self.request.POST, instance=event)
        else:
            raise ValueError('Operation not supported')
        if data.is_valid():
            event = data.save(commit=False)
            event.put()
            self.redirect("/admin/events")
        else:
            template_params = dict(events=Event.get_reversed_list(),
                    form=data, operation=operation)
            self.response.out.write(
                    template.render('templates/events_manager.html',
                        template_params))


class IndexPage(webapp.RequestHandler):

    def get(self):
        self.response.out.write(
                template.render(
                    'templates/index.html',
                    dict(events=Event.get_reversed_list())
                ))

class TestPage(webapp.RequestHandler):
    def get(self):
        locale.setlocale(locale.LC_ALL, 'fr_FR.UTF-8')
        d = datetime.strptime('12/12/1977', '%d/%m/%Y')
        s = d.strftime('%A %d %B %Y')
        self.response.out.write(s)


def main():
    logging.getLogger().setLevel(logging.DEBUG)
    application = webapp.WSGIApplication( [ 
                ('/', IndexPage), 
                ('/admin', AdminPage),
                ('/admin/events', EventsManager),
                ('/admin/events/delete', EventsDeleteHandler),
                ('/tests', TestPage),
                ], debug=True)
    wsgiref.handlers.CGIHandler().run(application)

if __name__ == "__main__":
    main()
