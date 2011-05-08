#!/usr/bin/env python
# -*- coding: UTF-8 -*-
from google.appengine.api import images
from base import RequestHandler, rfc3339date, log
from models import *
from datetime import datetime


class PageHandler(RequestHandler):
    def render_to_response(self, template_filename, **kw):
        super(PageHandler, self).render_to_response(template_filename, 
                links=Link.get_public_list(),
                tracks=Track.get_public_list(),
                year=datetime.today().year,
                **kw)


class IndexPage(PageHandler):

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
                next_page=next_page
                )




class TestPage(RequestHandler):

    def get(self):
        locale.setlocale(locale.LC_ALL, 'fr_FR.UTF-8')
        d = datetime.strptime('12/12/1977', '%d/%m/%Y')
        s = d.strftime('%A %d %B %Y')
        self.response.out.write(s)


class EventPage(PageHandler):

    def get(self, slug):
        event = Event.gql("WHERE slug = :1", slug).get()
        if event:
            self.render_to_response('public/event.html', event=event)
        else:
            self.error(404)

class PhotoGalleryHandler(PageHandler):
    def get(self):
        self.render_to_response('public/photo_gallery.html', photos=Image.all())


class AboutHandler(PageHandler):
    def get(self):
        self.render_to_response('public/about.html')


class EventImage(RequestHandler):
    def get(self, id):
        event = Event.get_by_id(int(id))
        if event.image:
            self.response.headers['Content-Type'] = "image/jpeg"
            self.response.out.write(event.image)
        else:
            self.error(404)


        


class PhotoHandler(RequestHandler):
    def get(self, key):
        image = Image.get(key)
        if image and image.image:
            self.response.headers['Content-Type'] = "image/jpeg"
            self.response.out.write(image.image)
        else:
            self.error(404)

class ThumbnailHandler(RequestHandler):
    def get(self, key):
        image = Image.get(key)
        if image and image.image:
            if not image.thumbnail:
                img = images.Image(image.image)
                img.resize(height=192)
                img.im_feeling_lucky()
                image.thumbnail = img.execute_transforms(output_encoding=images.JPEG)
                log.info("Creating thumbnail for %s", image.filename)
                image.put()
            self.response.headers['Content-Type'] = "image/jpeg"
            self.response.out.write(image.thumbnail)
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
