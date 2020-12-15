import os
from auth.auth import AuthError, requires_auth
from flask import Flask, request, abort, jsonify
from flask_cors import CORS
from .models import db, migrate, Actor, Movie

PAGINATION_SIZE = 10


def format_results(results):
    """Receive a SQLAlchemy results object and return it's results\
    wrapped in a python dictionary.

    :returns: array of Python formatted dictionary
    """
    return [item.format() for item in results]


def paginate(collection):
    """Return paginated array by size PAGNATION_SIZE. \
    If index is beyond valid point, return an empty array \
    (due to slicing of array)."""
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * PAGINATION_SIZE
    end = start + PAGINATION_SIZE
    return format_results(collection)[start:end]


TEST_DB_URI = ('postgresql+psycopg2://'
               'postgres:postgres@localhost:5432/agency_test')


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=False)

    if test_config is None:
        app.config.from_pyfile('config.py', silent=False)
    else:
        app.config.from_mapping(SECRET_KEY='dev',
                                SQLALCHEMY_DATABASE_URI=TEST_DB_URI,
                                SQLALCHEMY_TRACK_MODIFICATIONS=False,
                                DEBUG=True)

    db.init_app(app)
    migrate.init_app(app, db)

    CORS(app)

    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers',
                             'Content-Type, Authorization')
        response.headers.add('Access-Control-Allow-Methods',
                             'GET, POST, PATCH, DELETE, OPTIONS')
        return response

    # ==== App Routes =========
    @app.route('/actors', methods=['GET'])
    def get_actors():
        actors = Actor.query.all()
        paginated_actors = paginate(actors)
        if len(paginated_actors) < 1:  # empty array
            abort(404)
        return jsonify({
            'success': True,
            'total_actors': len(actors),
            'actors': paginated_actors
        })

    @app.route('/actors', methods=['POST'])
    @requires_auth('post:actors')
    def post_actors(jwt):
        body = request.get_json()
        new_name = body.get('name', None)
        new_age = body.get('age', None)
        new_gender = body.get('gender', None)

        try:
            actor = Actor(name=new_name, age=new_age, gender=new_gender)
            actor.insert()
            # Send back updated actors
            actors = Actor.query.order_by(Actor.id).all()
            # For now if the results return paginated: NBD
            current_actors = paginate(actors)
            return jsonify({
                'success': True,
                'created': actor.id,
                'actors': current_actors,
                'total_actors': len(actors)
            })
        except Exception:
            abort(422)

    @app.route('/actors/<int:actor_id>', methods=['DELETE', 'PATCH'])
    def delete_actor(actor_id):
        if request.method == 'DELETE':
            actor = Actor.query.filter(Actor.id == actor_id).one_or_none()
            if actor is None:
                abort(404)

            try:
                actor.delete()
                actors = Actor.query.all()
                current_actors = paginate(actors)
                return jsonify({
                    'success': True,
                    'deleted': actor_id,
                    'total_actors': len(actors),
                    'actors': current_actors
                })
            except Exception:
                abort(422)
        else:
            body = request.get_json()
            new_name = body.get("name", None)
            actor = Actor.query.filter(Actor.id == actor_id).one_or_none()
            if new_name is not None:
                actor.name = new_name
                actor.insert()
            else:
                abort(400)

            actors = Actor.query.all()
            return jsonify({
                'success': True,
                'actors': format_results(actors)
            })

    @app.route('/movies/<int:movie_id>', methods=['PATCH'])
    def update_movie(movie_id):
        movie = Movie.query.filter(Movie.id == movie_id).one_or_none()
        if movie is None:
            abort(404)

        body = request.get_json()
        new_title = body.get("title", None)

        if new_title is not None:
            movie.title = new_title
            movie.insert()
        else:
            abort(400)

        movies = Movie.query.all()
        return jsonify({
            'success': True,
            'movies': format_results(movies)
        })

    @app.route('/movies', methods=['GET'])
    def get_movies():
        movies = Movie.query.all()
        paginated_movies = paginate(movies)
        if len(paginated_movies) < 1:  # empty array
            abort(404)
        return jsonify({
            'success': True,
            'movies': paginated_movies,
            'total_movies': len(movies)
        })

    @app.route('/actors/<int:actor_id>/movies', methods=['GET'])
    @requires_auth('get:movies')
    def get_actor_movies(jwt, actor_id):
        actor = Actor.query.filter(Actor.id == actor_id).one_or_none()
        if actor is None:
            abort(404)
        formatted_movies = format_results(actor.movies)
        return jsonify({
            'success': True,
            'total_movies': len(formatted_movies),
            'actor': actor.id,
            'movies': formatted_movies,
        })

    @app.route('/actors/<int:actor_id>/movies', methods=['POST'])
    @requires_auth('post:movies')
    def post_actor_movies(jwt, actor_id):
        body = request.get_json()
        new_title = body.get('title', None)
        new_release_date = body.get('release_date', None)
        try:
            movie = Movie(title=new_title, release_date=new_release_date)
            movie.insert()
        except Exception:
            abort(422)

        actor = Actor.query.filter(Actor.id == actor_id).one_or_none()
        if actor is None:
            abort(404)
        actor.movies.append(movie)
        actor.insert()

        formatted_movies = format_results(actor.movies)
        return jsonify({
            'success': True,
            'created': movie.id,
            'movies': formatted_movies,
            'total_movies': len(formatted_movies)
        })

    @app.route('/actors/<int:actor_id>/movies/<int:movie_id>',
               methods=['DELETE'])
    def delete_movie_from_actor(actor_id, movie_id):
        actor = Actor.query.filter(Actor.id == actor_id).one_or_none()
        if actor is None:
            abort(404)
        movie_to_del = Movie.query.filter(Movie.id == movie_id).one_or_none()
        if movie_to_del is None:
            abort(404)
        actor.movies.remove(movie_to_del)
        db.session.commit()

        movies = Movie.query.all()
        return jsonify({
            'success': True,
            'deleted': movie_id,
            'movies': format_results(movies),
            'total_movies': len(movies)
        })

    # ==== Error Handling =======
    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": "unprocessable"
        }), 422

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": "resource not found"
        }), 404

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "success": False,
            "error": 400,
            "message": "bad request"
        }), 400

    @app.errorhandler(401)
    def unauthorized(error):
        return jsonify({
            'success': False,
            "error": 401,
            "message": 'unauthorized'
        }), 401

    @app.errorhandler(405)
    def not_allowed(error):
        return jsonify({
            'success': False,
            'error': 405,
            'message': "method not allowed"
        })

    @app.errorhandler(AuthError)
    def jwt_errors(auth_error):
        response = jsonify(auth_error.error)
        response.status_code = auth_error.status_code
        return response

    return app
