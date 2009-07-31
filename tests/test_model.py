from . import BaseTest
from main import Link

class TestModels(BaseTest):

    def test_link(self):
        url = "http://example.com"
        link = Link(url=url)
        link.put()
        self.assertEqual(Link.gql("WHERE url = :1", url).count(), 1)

