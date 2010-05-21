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

    def test_populate_event(self):
        location = 'bar'
        event = Event(title='Hello World Event', location=location,
                            date='2009-01-25')
        expected_slug = u'25-01-2009_hello-world-event'
        event.put()
        event = Event.gql("WHERE slug = '%s'" % str(expected_slug)).get()
        assert event.location == location

    def test_prolematic_slug(self):
        location = 'bar'
        event = Event(title='Festipop 2010 avec Roots League, Lion Roots et ...  Iration Steppas !', location=location,
                            date='2010-05-28')
        expected_slug = u'28-05-2010_festipop-2010-avec-roots-league-lion-roots-et-iration-steppas'
        event.put()
        self.assertEqual(event.slug, expected_slug)
