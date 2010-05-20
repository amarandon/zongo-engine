#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import re

from datetime import datetime
from google.appengine.ext import db
from base import Model, rfc3339date, ImageFileProperty, classproperty

class Link(Model):
    title = db.StringProperty(default=" ", 
            verbose_name='Titre')
    url = db.StringProperty(required=True)

    verbose_name = 'lien'
    verbose_name_plural = 'liens'

    code_name = 'link'
    code_name_plural = 'links'

    position = db.IntegerProperty(default=0)

    visible_properties = ('position', 'title', 'url', 'published')

    def __init__(self, parent=None, key_name=None, **kw):
        Model.__init__(self, parent=parent, key_name=key_name, **kw)


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



class StrDateTimeProperty(db.Property):

    def get_value_for_form(self, instance):
        """Extract the property value from the instance for use in a form.

            Override this to do a property- or field-specific type conversion.

            Args:
              instance: a db.Model instance

            Returns:
              The property's value extracted from the instance, possibly
              converted to a type suitable for a form field; possibly None.

            By default this returns the instance attribute's value unchanged.
        """
        return getattr(instance, self.name).strftime("%d/%m/%Y")

    def make_value_from_form(self, value):
        """Convert a form value to a property value.

            Override this to do a property- or field-specific type conversion.

            Args:
              value: the cleaned value retrieved from the form field

            Returns:
              A value suitable for assignment to a model instance's property;
              possibly None.

            By default this converts the value to self.data_type if it
            isn't already an instance of that type, except if the value is
            empty, in which case we return None.
        """
        if value in (None, ''):
            return None
        if not isinstance(value, self.data_type):
            value = datetime.strptime(value, "%d/%m/%Y")
        return value

class Image(Model):
    image = ImageFileProperty()
    thumbnail = db.BlobProperty()
    filename = db.StringProperty(required=True)
    title = db.StringProperty(required=True)
    credit = db.StringProperty()
    description = db.TextProperty()
    visible_properties = ('filename', 'title', 'description', 'credit', 'published')

    code_name = 'image'
    code_name_plural = 'images'

    @classproperty
    def verbose_name(cls):
        return cls.code_name

    @classproperty
    def verbose_name_plural(cls):
        return cls.code_name_plural

class Event(Model):
    date = StrDateTimeProperty(required=True)
    location = db.StringProperty(required=True, verbose_name='Lieu')
    title = db.StringProperty(required=True, 
            verbose_name='Intitulé (pour le feed Atom)')
    slug = db.StringProperty()
    description = db.TextProperty()
    image = ImageFileProperty()
    small_image = db.BlobProperty()

    verbose_name = 'événement'
    verbose_name_plural = 'événements'

    code_name = 'event'
    code_name_plural = 'events'

    visible_properties = ('date', 'location', 'title', 'description', 'published')

    def __init__(self, parent=None, key_name=None, **kw):
        Model.__init__(self, parent=parent, key_name=key_name, **kw)

    def set_slug(self):
        # TODO: detect duplicate
        slug = self.title.replace(u'é', 'e').replace(u'à', 'a').replace(u'è',
                'e').replace(u'ê', 'e')
        slug = slug[:50]
        slug = re.sub("[^A-Za-z0-1-]", "-", slug)
        slug = slug.lower()
        if isinstance(self.date, datetime):
            year, month, day = self.date.year, self.date.month, self.date.day
        else:
            year, month, day = [int(part) for part in self.date.split("-")]
        self.slug = '%02d-%02d-%04d_%s' % (day, month, year, slug)

    def put(self, **kw):
        self.set_slug()
        Model.put(self, **kw)

    @property
    def formatted_date(self):
        day = self.date.day
        if day == 1:
            day = '1er'
        month = MOIS[int(self.date.month) - 1]
        weekday = JOURS[self.date.weekday()]
        return "%s %s %s %s" % (weekday, day, month, self.date.year)

    @property
    def formatted_location(self):
        return self.location.replace('&', '&amp;')

    @property
    def formatted_description(self):
        paragraphs = ["<p>%s</p>" % p for p in self.description_paragraphs] 
        return ''.join(paragraphs)

    @property
    def description_paragraphs(self):
        description = self.description.replace('&', '&amp;')
        return description.split('\r\n\r\n')

    @property
    def short_description(self):
        return ' '.join(self.description.split()[:100]) + ' (...)'

    @property
    def url(self):
        return self.date.strftime("%Y/%m/%d") + '/' + str(self.id)

    @property
    def atom_updated_at(self):
        return rfc3339date(self.updated_at)


    @classmethod
    def get_reversed_list(cls, page_size, page):
        query = cls.gql("WHERE published = True ORDER BY date DESC")
        return query.fetch(page_size, offset=((page - 1) * page_size))

