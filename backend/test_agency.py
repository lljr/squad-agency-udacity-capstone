import unittest
import json
from agency import create_app
from mock_data import mock_actors
from agency.models import db, Actor


class AgencyTestCase(unittest.TestCase):
    """This class represents the test cases for Agency."""

    def setUp(self):
        self.app = create_app(test_config=True)
        self.client = self.app.test_client

        self.ctx = self.app.app_context()
        self.ctx.push()

        self.db = db
        self.db.init_app(self.app)
        with self.app.app_context():
            self.db.create_all()

        # Mock data setup
        self.mock_actors = mock_actors

    def tearDown(self):
        with self.app.app_context():
            self.db.session.remove()
            self.db.drop_all()
        self.ctx.pop()

    def test_get_all_actors(self):
        """Test that all actors exist in the database."""
        # Set up route with mock data
        for actor in self.mock_actors:
            actor = Actor(**actor)
            actor.insert()

        res = self.client().get('/actors')

        self.assertEqual(res.status_code, 200)
        self.assertEqual("application/vnd.api+json", res.mimetype)

        data = json.loads(res.data)
        self.assertTrue(len(data['data']))


if __name__ == "__main__":
    unittest.main()
