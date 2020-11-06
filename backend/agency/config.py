import os
SECRET_KEY = os.urandom(32)
SQLALCHEMY_DATABASE_URI = "postgresql://postgres:postgres@localhost:5432/agency"
SQLALCHEMY_TRACK_MODIFICATIONS = False
