from main import Link
from . import BaseTest

class TestHandlers(BaseTest):

    def test_index(self):
        response = self.app.get('/')
        assert 'Zongo' in str(response)

    def test_admin(self):
        response = self.app.get('/admin')
        assert response





