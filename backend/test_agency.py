import unittest
import json
from flask_sqlalchemy import SQLAlchemy
from agency import create_app
from agency.models import db, Actor


class AgencyTestCase(unittest.TestCase):
    """This class represents the test cases for Agency."""

    def setUp(self):
        self.app = create_app(test_config=True)
        self.client = self.app.test_client

        ctx = self.app.app_context()
        ctx.push()

        self.db = db
        self.db.init_app(self.app)
        with self.app.app_context():
            self.db.create_all()

    def tearDown(self):
        with self.app.app_context():
            self.db.session.remove()
            self.db.drop_all()

    def test_get_all_actors(self):
        res = self.client().get('/actors')

        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertEqual("application/vnd.api+json", data.mimetype)


if __name__ == "__main__":
    unittest.main()
