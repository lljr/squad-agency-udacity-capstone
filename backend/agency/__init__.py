import os
from auth.auth import AuthError, requires_auth
from flask import Flask, request, abort, jsonify
from flask_cors import CORS
from .models import db, migrate, Actor, Movie

PAGINATION_SIZE = 10


def format_results(results):
    """Receive a SQLAlchemy results object and return it's results\
    wraipped in a python dictionary.

    :returns: array of Python formatted dictionary
    """
    return [item.format() for item in results]


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=False)

    if test_config is None:
        app.config.from_pyfile('config.py', silent=False)
    else:
        app.config.from_mapping(SECRET_KEY='dev',
                                SQLALCHEMY_DATABASE_URI=os.path.join(
                                    "sqlite:///" + app.instance_path,
                                    'agency.sqlite'),
                                SQLALCHEMY_TRACK_MODIFICATIONS=False,
                                DEBUG=True)

    db.init_app(app)
    migrate.init_app(app, db)

    CORS(app)

    # ensure app instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

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
        page = request.args.get('page', 1, type=int)
        start = (page - 1) * PAGINATION_SIZE
        end = start + PAGINATION_SIZE
        actors = Actor.query.all()
        return jsonify({
            'success': True,
            'total_actors': len(actors),
            'actors': format_results(actors)[start:end]
        })

    @app.route('/movies')
    def get_movies():
        page = request.args.get('page', 1, type=int)
        start = (page - 1) * PAGINATION_SIZE
        end = start + PAGINATION_SIZE
        movies = Movie.query.all()
        return jsonify({
            'success': True,
            'movies': format_results(movies)[start:end],
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
