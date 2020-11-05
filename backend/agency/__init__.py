from flask import Flask, request, jsonify, abort
from model import db, migrate, Actor, Movie
from flask_cors import CORS


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

    return app
