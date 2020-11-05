from flask import Flask
from model import db, migrate


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

    @app.route('/hello')
    def hello():
        pass

    return app
