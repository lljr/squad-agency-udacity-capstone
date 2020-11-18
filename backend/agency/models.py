from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy()
migrate = Migrate()

assigned_movies = db.Table(
    'assigned_movies',
    db.Column('actor_id',
              db.Integer,
              db.ForeignKey('actor.id'),
              primary_key=True),
    db.Column('movie_id',
              db.Integer,
              db.ForeignKey('movie.id'),
              primary_key=True))


class Actor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    age = db.Column(db.Integer)
    gender = db.Column(db.String(1))

    movies = db.relationship('Movie',
                             secondary=assigned_movies,
                             backref=db.backref('actors', lazy=True))

    def format(self):
        return {
            'id': self.id,
            'name': self.name,
            'age': self.age,
            'gender': self.gender,
        }

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


class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    release_date = db.Column(db.DateTime, nullable=False)

    def format(self):
        return {
            'id': self.id,
            'title': self.title,
            'release_date': self.release_date
        }

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
