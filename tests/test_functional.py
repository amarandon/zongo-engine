from main import Link, Event
from . import BaseTest

class TestHandlers(BaseTest):

    def test_index(self):
        response = self.app.get('/')
        assert 'Zongo' in response

    def test_admin(self):
        response = self.app.get('/admin')
        assert response

    def test_published_link(self):
        url = "http://example.com"
        Link(url=url, published=True).put()
        assert url in self.app.get('/')

    def test_not_published_link(self):
        url = "http://example.com"
        Link(url=url).put()
        assert url not in self.app.get('/')
        assert url in self.app.get('/admin/links')

    def test_published_event(self):
        location = 'Somewhere'
        Event(date=self.str2date('2009-01-01'), location=location, published=True).put()
        response = self.app.get('/')
        assert location in response

    def test_not_published_event(self):
        location = 'Somewhere'
        Event(date=self.str2date('2009-01-01'), location=location).put()
        assert location not in self.app.get('/')
        assert location in self.app.get('/admin/events')
