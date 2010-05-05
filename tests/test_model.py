from . import BaseTest
from main import Link, Event

class TestModels(BaseTest):

    def test_link(self):
        url = "http://example.com"
        link = Link(url=url)
        link.put()
        self.assertEqual(Link.gql("WHERE url = :1", url).count(), 1)

    def test_main_image(self):
        event = Event(title='foo', location='bar', date='2009-01-01')
        event.put()

    def test_populate_link(self):
        location = 'bar'
        event = Event(title='Hello World Event', location=location,
                            date='2009-01-25')
        expected_slug = u'25-01-2009_hello-world-event'
        event.put()
        event = Event.gql("WHERE slug = '%s'" % str(expected_slug)).get()
        assert event.location == location
