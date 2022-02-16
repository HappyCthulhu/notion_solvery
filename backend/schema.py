from flask_marshmallow import Marshmallow
from marshmallow import fields, Schema

from backend.models import NewNotionPages
from app import app

# marshmello должен быть иницианизирован после sql_alchemy
ma = Marshmallow(app)


class NewPagesSchema(ma.Schema):
    class Meta:
        model = NewNotionPages

    # TODO: понять, как сделать auto_value и SQLAlchemyAutoSchema. Чтоб не приходилось прописывать значение полей, чтоб оно само это делало
    title = ma.String()
    page_url = ma.String()


# class AllNotionPages():


class BookmarksSchema(Schema):
    class BookmarksForRemove():
        id = fields.Integer(dump_only=True, required=True)
