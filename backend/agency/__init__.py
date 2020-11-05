from auth.auth import AuthError, requires_auth
from flask import Flask, request, jsonify, abort
from model import db, migrate, Actor, Movie
from flask_cors import CORS


def J(*args, **kwargs):
    """Wrapper around jsonify that sets the Content-Type of the response to
    application/vnd.api+json.
    """
    response = jsonify(*args, **kwargs)
    response.mimetype = "application/vnd.api+json"
    return response

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)

    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE_URI="postgresql://postgres:postgres@localhost:5432/agency_test",
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        DEBUG=True
    )

    if test_config in None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)
        with app.app_context():
            db.app = app
            db.init_app(app)
            migrate.init_app(app, db)

    CORS(app)

    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Header',
                             'Content-Type, Authorization')
        response.headers.add('Access-Control-Allow-Methods',
                             'GET, POST, PATCH, DELETE, OPTIONS')
        return response

    @app.route('/hello')
    def hello():
        pass

        # ====Error Handling=======
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
