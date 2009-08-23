import os
import logging
log = logging.getLogger()
log.setLevel(logging.DEBUG)

from google.appengine.ext import webapp
from google.appengine.ext import db
from django.template.loader import render_to_string

class classproperty(object):

    def __init__(self, func):
        self.func = func

    def __get__(self, instance, owner):
        return self.func(owner)


def rfc3339date(datetime):
    return datetime.strftime("%Y-%m-%dT%H:%M:%SZ")


class Model(db.Model):

    created_at = db.DateTimeProperty(auto_now_add=True)
    updated_at = db.DateTimeProperty(auto_now=True)
    atom_id = db.StringProperty()
    published = db.BooleanProperty(default=False, verbose_name="Publier")

    def __init__(self, parent=None, key_name=None, **kw):
        db.Model.__init__(self, parent=parent, key_name=key_name, **kw)
        self.atom_id = self.build_atom_id()

    @classproperty
    def admin_url(cls):
        name = cls.__name__.lower()
        url = '/admin/%ss' % name
        return url


    @classmethod
    def get_public_list(cls):
        return cls.get_ordered_list().filter("published =", True)

    @classmethod
    def get_ordered_list(cls):
        query = db.Query(cls)
        if hasattr(cls, 'position'):
            return query.order('position')
        else:
            return query.order('-updated_at')

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
    def formatted_published(self):
        return 'Oui' if self.published is True else 'Non'


class RequestHandler(webapp.RequestHandler):

    def render_to_response(self, template_filename, **kw):
        if 'SERVER_SOFTWARE' in os.environ and \
                os.environ['SERVER_SOFTWARE'].startswith('Development'):
            kw['dev_environment'] = True
        else:
            kw['dev_environment'] = False
        output = render_to_string(template_filename, kw)
        self.response.out.write(output)
