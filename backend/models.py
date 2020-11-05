from sqlalchemy import (Column, String, Integer, DateTime, Table, ForeignKey)
from sqlalchemy.ext.declarative import declarative_base
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate


db = SQLAlchemy()
migrate = Migrate()


Base = declarative_base()
Base.query = db.session.query_property()

actor_items = Table(
    'association',
    Base.metadata,
    Column('actor_id', Integer, ForeignKey('actor.id'), primary_key=True),
    Column('movie_id', Integer, ForeignKey('movie.id'), primary_key=True)
)


class Actor(Base):
    __tablename__ = "actor"
    id = Column(Integer, primary_key=True)
    name = Column(String(120))
    age = Column(Integer)
    gender = Column(String(1))
    movies = db.relationship('Movie',
                             secondary=actor_items,
                             backref=db.backref('actors', lazy=True))

    def insert(self):
        """Inserts a new model into the database."""
        db.session.add(self)
        db.session.commit()

    def delete(self):
        """Deletes a model from the database."""
        db.session.delete(self)
        db.session.commit()

    def update(self):
        """Updates an existing model in the database."""
        db.session.commit()


class Movie(Base):
    __tablename__ = "movie"
    id = Column(Integer, primary_key=True)
    title = Column(String(200), nullable=False)
    release_date = Column(DateTime, nullable=False)

    def insert(self):
        """
        Inserts a new model into the database.
        """
        db.session.add(self)
        db.session.commit()

    def delete(self):
        """Deletes a model from the database."""
        db.session.delete()
        db.session.commit()

    def update(self):
        """Updates an existing model in the database."""
        db.session.commit()
