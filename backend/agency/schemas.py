from marshmallow import validate
from marshmallow_jsonapi import fields
from marshmallow_jsonapi.flask import Relationship, Schema


class MovieSchema(Schema):
    id = fields.Str(dump_only=True)
    title = fields.Str(validate=validate.Length(200))
    release_date = fields.DateTime(required=True)

    class Meta:
        type_ = "movies"
        # self_view = "movie_detail"
        # self_view_kwargs = {"movie_id": "<id>", "_external": True}
        self_view_many = "get_movies"


class ActorSchema(Schema):
    id = fields.Str(dump_only=True)
    name = fields.Str(required=True)
    age = fields.Integer(required=True)
    gender = fields.Str(validate=validate.Length(1))
    movies = Relationship(
        # TODO add view names
        related_view="",
        related_view_kwargs="",
        many=True,
        include_data=True,
        type_="movies"
    )

    class Meta:
        type_ = "actors"
        # self_view = "actor_detail"
        # self_view_kwargs = {"actor_id": "<id>"}
        self_view_many = "get_actors"
