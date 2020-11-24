import unittest
import json
from agency import create_app, PAGINATION_SIZE
from mock_data import mock_actors, mock_movies
from agency.models import db, Actor, Movie


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
        self.mock_movies = mock_movies

    def tearDown(self):
        with self.app.app_context():
            self.db.session.remove()
            self.db.drop_all()
        self.ctx.pop()

    def test_get_paginated_actors(self):
        """Test actors pagination."""
        # Set up route with mock data
        for actor_args in self.mock_actors:
            actor = Actor(**actor_args)
            actor.insert()

        res = self.client().get('/actors')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_actors'])
        self.assertEqual(len(data['actors']), PAGINATION_SIZE)

    def test_404_sent_requesting_beyond_valid_actors_page(self):
        for actor_args in self.mock_actors:
            actor = Actor(**actor_args)
            actor.insert()

        res = self.client().get('/actors?page=100000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)

    def test_get_paginated_movies(self):
        """Test movies pagination."""
        for movie_args in self.mock_movies:
            movie = Movie(**movie_args)
            movie.insert()

        res = self.client().get('/movies')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_movies'])
        self.assertEqual(len(data['movies']), PAGINATION_SIZE)

    def test_404_sent_requesting_beyond_valid_movies_page(self):
        for movie_args in self.mock_movies:
            movie = Movie(**movie_args)
            movie.insert()

        res = self.client().get('/movies?page=100000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)


if __name__ == "__main__":
    unittest.main()
