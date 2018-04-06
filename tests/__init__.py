import unittest
from gradient import create_app, db

test_config = {
    'TESTING': True,
    'WTF_CSRF_ENABLED': False,
    'SQLALCHEMY_DATABASE_URI': 'postgresql://gradient_user:password@localhost:5432/gradient_test',
    'SECURITY_PASSWORD_HASH': 'plaintext'
}


class Base(unittest.TestCase):
    def __call__(self, result=None):
        """Sets up the tests without needing to call `setUp`."""
        self._pre_setup()
        try:
            self._pre_setup()
            super().__call__(result)
        finally:
            self._post_teardown()

    def _pre_setup(self):
        self.app = create_app(**test_config)
        self.client = self.app.test_client()

        self._ctx = self.app.test_request_context()
        self._ctx.push()

        self.db = db
        with self.app.app_context():
            self.db.drop_all()
            self.db.create_all()

    def _post_teardown(self):
        if self._ctx is not None:
            self._ctx.pop()

        with self.app.app_context():
            self.db.session.remove()
            self.db.drop_all()

        del self.app
        del self.client
        del self._ctx