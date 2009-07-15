#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from google.appengine.ext import db
from base import Model, rfc3339date

class Link(Model):
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



class Event(Model):
    date = db.DateTimeProperty(required=True)
    location = db.StringProperty(required=True, verbose_name='Lieu')
    title = db.StringProperty(default=" ", 
            verbose_name='Intitulé (optionnel)')
    description = db.TextProperty(default=" ")
    image = db.BlobProperty()
    small_image = db.BlobProperty()

    verbose_name = 'événement'
    verbose_name_plural = 'événements'

    code_name = 'event'
    code_name_plural = 'events'

    visible_properties = ('date', 'location', 'title', 'description', 'live')

    def __init__(self, parent=None, key_name=None, **kw):
        Model.__init__(self, parent=parent, key_name=key_name, **kw)

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

    @property
    def atom_updated_at(self):
        return rfc3339date(self.updated_at)


    @classmethod
    def get_reversed_list(cls):
        return cls.gql("ORDER BY date DESC")

