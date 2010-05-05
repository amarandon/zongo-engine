from main import Link, Event
from . import BaseTest

class TestViewHandlers(BaseTest):

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
        Event(title='foo', date=self.str2date('2009-01-01'), location=location, published=True).put()
        response = self.app.get('/')
        assert location in response

    def test_not_published_event(self):
        location = 'Somewhere'
        Event(title='foo', date=self.str2date('2009-01-01'), location=location).put()
        assert location not in self.app.get('/')
        assert location in self.app.get('/admin/events')

    def test_missing_event_page(self):
        response = self.app.get('/events/missingapsdjhfaljsk', status=404)

    def test_event_page(self):
        location = 'Somewhere'
        title = "This+is*a;weird Title"
        event = Event(title=title, date=self.str2date('2009-01-31'), location=location,
                published=True)
        event.put()
        slug = "31-01-2009-this-is-a-weird-title"
        self.assertEqual(event.slug, slug)
        response = self.app.get('/events/%s' % slug)
        assert location in response, location + ' should be in ' + response.body

class TestAdminHandlers(BaseTest):

    def test_create_event(self):
        form = self.app.get('/admin/events/new').form
        form['title'] = 'This is a test event'
        form['date'] = '25/01/2000'
        form['image'] = ('cows.jpg', open('tests/small_cows.jpg').read())
        form['description'] = 'great event'
        form['location'] = 'Tokyo'
        response = form.submit()

        event = Event.gql("WHERE title = :1", 'This is a test event').get()
        self.assertEqual(event.description, 'great event')
        self.assertEqual(event.location, 'Tokyo')
        self.assertEqual(event.date.day, 25)
        assert event.image
