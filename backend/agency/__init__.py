import os
from auth.auth import AuthError, requires_auth
from flask import Flask, request, abort, jsonify
from flask_cors import CORS
from .models import db, migrate, Actor, Movie
from .schemas import ActorSchema, MovieSchema


def J(*args, **kwargs):
    """Wrapper around jsonify that sets the Content-Type of the response to
    application/vnd.api+json.
    """
    response = jsonify(*args, **kwargs)
    response.mimetype = "application/vnd.api+json"
    return response


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=False)

    if test_config is None:
        app.config.from_pyfile('config.py', silent=False)
    else:
        app.config.from_mapping(SECRET_KEY='dev',
                                SQLALCHEMY_DATABASE_URI=os.path.join(
                                    "sqlite:///" + app.instance_path, 'agency.sqlite'),
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
        response.headers.add('Access-Control-Allow-Header',
                             'Content-Type, Authorization')
        response.headers.add('Access-Control-Allow-Methods',
                             'GET, POST, PATCH, DELETE, OPTIONS')
        return response

    # ==== App Routes =========
    @app.route('/actors')
    def get_actors():
        actors = Actor.query.all()
        data = ActorSchema(many=True).dump(actors)
        return J(data)

    @app.route('/movies')
    def get_movies():
        return jsonify({
            'success': True
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

    @app.errorhandler(AuthError)
    def jwt_errors(auth_error):
        response = jsonify(auth_error.error)
        response.status_code = auth_error.status_code
        return response

    return app
