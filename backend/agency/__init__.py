from flask import Flask


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

    @app.route('/hello')
    def hello():
        pass

    return app