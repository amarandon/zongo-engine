#!/usr/bin/env python
# -*- coding: UTF-8 -*-
from google.appengine.api import images
from base import RequestHandler, rfc3339date, log
from models import *
from datetime import datetime


class IndexPage(RequestHandler):

    def get(self):
        page_size = 5
        page = int(self.request.get('page', 1))
        next_page = previous_page = 0

        if page > 1:
            next_page = page - 1

        count = Event.all().count()
        if page * page_size < count:
            previous_page = page + 1

        self.render_to_response('public/index.html', 
                events=Event.get_reversed_list(page_size, page),
                previous_page=previous_page,
                next_page=next_page,
                links=Link.get_public_list(),
                tracks=Track.get_public_list(),
                year=datetime.today().year
                )


class TestPage(RequestHandler):

    def get(self):
        locale.setlocale(locale.LC_ALL, 'fr_FR.UTF-8')
        d = datetime.strptime('12/12/1977', '%d/%m/%Y')
        s = d.strftime('%A %d %B %Y')
        self.response.out.write(s)


class EventPage(RequestHandler):

    def get(self, slug):
        event = Event.gql("WHERE slug = :1", slug).get()
        if event:
            self.render_to_response('public/event.html', 
                    event=event,
                    links=Link.get_public_list(),
                    tracks=Track.get_public_list(),
                    year=datetime.today().year
                    )
        else:
            self.error(404)


class EventImage(RequestHandler):
    def get(self, id):
        event = Event.get_by_id(int(id))
        if event.image:
            self.response.headers['Content-Type'] = "image/jpeg"
            self.response.out.write(event.image)
        else:
            self.error(404)

class EventImageFromSlug(RequestHandler):
    def get(self, slug):
        event = Event.gql("WHERE slug = :1", slug).get()
        if event and event.image:
            self.response.headers['Content-Type'] = "image/jpeg"
            self.response.out.write(event.image)
        else:
            self.error(404)


class EventSmallImage(RequestHandler):
    def get(self, id):
        event = Event.get_by_id(int(id))
        if event.image:
            if not event.small_image:
                image = images.Image(event.image)
                max_size = image.width if image.width > image.height else image.height
                small_size = 250.0
                if small_size < max_size:
                    ratio = small_size / max_size
                    image.resize(int(image.width * ratio), int(image.height * ratio))
                    log.info("Creating small event image")
                    event.small_image = image.execute_transforms(output_encoding=images.JPEG)
                else:
                    event.small_image = event.image
                event.put()


            self.response.headers['Content-Type'] = "image/jpeg"
            self.response.out.write(event.small_image)
        else:
            self.error(404)


class EventsFeed(RequestHandler):
    def get(self):
        event_list = Event.get_reversed_list(10, 1)
        updated_at_list = [event.updated_at for event in event_list]
        latest_updated_at = rfc3339date(max(updated_at_list))

        self.response.headers['Content-Type'] = "application/atom+xml"
        self.render_to_response('atom.xml', 
                events=event_list,
                host_url=self.request.host_url,
                updated_at=latest_updated_at
                )
