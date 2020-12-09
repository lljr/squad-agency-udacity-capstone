import unittest
import json
import os
import sys
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

        self.new_actor = mock_actors[0]
        self.new_movie = mock_movies[0]

        # Auth tokens
        self.assistant = os.environ.get('ASSISTANT_TOKEN', None)
        if self.assistant is None:
            print("ASSISTANT_TOKEN environment variable not set.")
            sys.exit()
        self.director = os.environ.get('DIRECTOR_TOKEN', None)
        if self.director is None:
            print("DIRECTOR_TOKEN environment variable not set.")
        self.producer = os.environ.get('PRODUCER_TOKEN', None)
        if self.producer is None:
            print("PRODUCER_TOKEN environment variable not set.")

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

    def test_create_new_actor(self):
        res = self.client().post('/actors', json=self.new_actor)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['created'], 1)
        self.assertTrue(data['actors'])
        self.assertTrue(data['total_actors'])

    def test_422_create_actor_fails(self):
        res = self.client().post('/actors', json={
            'name': 'Pete',
            'age': 33,
            'gender': 23,
        })

        # data = json.loads(res.data)
        self.assertEqual(res.status_code, 422)

    def test_delete_an_actor(self):
        for actor_args in self.mock_actors:
            actor = Actor(**actor_args)
            actor.insert()

        res = self.client().delete('/actors/1')
        data = json.loads(res.data)

        deleted_actor = Actor.query.filter(Actor.id == 1).one_or_none()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(deleted_actor, None)
        self.assertEqual(data['deleted'], 1)
        self.assertTrue(data['total_actors'])
        self.assertTrue(len(data['actors']))

    def test_404_send_delete_non_existing_actor(self):
        res = self.client().delete('/actors/99999')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)

    def test_get_actors_movie(self):
        # Set up
        actor = Actor(**self.new_actor)
        actor.insert()

        movie = Movie(**self.new_movie)
        movie.insert()

        actor.movies.append(movie)
        db.session.commit()

        res = self.client().get(
            '/actors/1/movies',
            headers={'Authorization': f"Bearer {ASSISTANT_TOKEN}"},
            json=self.new_movie)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_movies'])
        self.assertTrue(len(data['movies']))
        self.assertEqual(data['actor'], 1)

    def test_get_non_existing_actor_movies(self):
        # Set up
        res = self.client().get(
            '/actors/99999/movies',
            headers={'Authorization': f"Bearer {ASSISTANT_TOKEN}"})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)

    def test_create_new_movie(self):
        actor = Actor(**self.new_actor)
        actor.insert()

        res = self.client().post(
            'actors/1/movies',
            json=self.new_movie,
            headers={'Authorization': f"Bearer {PRODUCER_TOKEN}"})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['created'], 1)
        self.assertTrue(data['movies'])
        self.assertEqual(data['total_movies'], 1)

    def test_404_creating_movie_on_non_existing_actor(self):
        res = self.client().post('/actors/9999/movies',
                                 json=self.new_movie,
                                 headers={
                                     'Authorization': f"Bearer {PRODUCER_TOKEN}"
                                 })
        data = json.loads(res.data)

        self.assertEqual(data['success'], False)
        self.assertEqual(res.status_code, 404)

    def test_422_create_movie_with_incorrect_data_type(self):
        actor = Actor(**self.new_actor)
        actor.insert()

        res = self.client().post(
            'actors/1/movies',
            json={
                'title': 'A title',
                'release_date': 83223
            },
            headers={'Authorization': f"Bearer {PRODUCER_TOKEN}"})

        data = json.loads(res.data)
        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)

    def test_delete_movie_related_to_actor(self):
        # Setup
        actor = Actor(**self.new_actor)

        movie = Movie(**self.new_movie)
        movie.insert()

        actor.movies.append(movie)
        actor.insert()

        self.assertEqual(len(actor.movies), 1)

        res = self.client().delete('/actors/1/movies/1')
        data = json.loads(res.data)

        actor_without_movies = Actor.query.get(1)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted'], 1)
        self.assertEqual(len(actor_without_movies.movies), 0)
        self.assertTrue(len(data['movies']))
        self.assertTrue(data['total_movies'])

    def test_404_deleting_non_existing_movie(self):
        actor = Actor(**self.new_actor)
        actor.insert()

        res = self.client().delete('actors/1/movies/9999')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)

    def test_404_attempt_to_delete_non_existing_actor_with_movie(self):
        res = self.client().delete('actors/99999/movies/1')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)

    def test_updating_actor(self):
        # Setup
        actor = Actor(**self.new_actor)
        actor.insert()

        res = self.client().patch('/actors/1', json={'name': 'Bobi'})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['actors']))

        updated_actor = Actor.query.get(1)
        self.assertEqual(updated_actor.name, 'Bobi')

    def test_400_bad_request_sent_updating_actor(self):
        res = self.client().patch('/actors/1', json={})
        self.assertEqual(res.status_code, 400)

    def test_updating_movie(self):
        movie = Movie(**self.new_movie)
        movie.insert()

        res = self.client().patch('/movies/1', json={'title': 'new title'})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['movies']))

        updated_movie = Movie.query.get(1)
        self.assertEqual(updated_movie.title, 'new title')

    def test_404_update_non_existing_movie(self):
        res = self.client().patch('/movies/9999', json={'title': 'new'})

        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)

    def test_400_bad_request_sent_updating_movie(self):
        movie = Movie(**self.new_movie)
        movie.insert()

        res = self.client().patch('/movies/1', json={})
        self.assertEqual(res.status_code, 400)

    # def test_assistant_cannot_create_new_actor(self):
    #     res = self.client().post(
    #         '/actors',
    #         json=self.new_actor,
    #         headers={'Authorization': f"Bearer {ASSISTANT_TOKEN}"})
    #     data = json.loads(res.data)
    #     self.assertEqual(res.status_code, 403)
    #     self.assertEqual(data['code'], 'unauthorized')


if __name__ == "__main__":
    unittest.main()
