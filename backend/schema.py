from flask_marshmallow import Marshmallow
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema, auto_field

from backend.models import NewNotionPages, BookmarksForRemove


# marshmello должен быть иницианизирован после sql_alchemy
ma = Marshmallow()


class NewPagesSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = NewNotionPages

    # TODO: понять, как сделать auto_value и SQLAlchemyAutoSchema. Чтоб не приходилось прописывать значение полей, чтоб оно само это делало
    link = auto_field(dump_only=True)
    title = auto_field(dump_only=True)


# class AllNotionPages():


class BookmarksSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = BookmarksForRemove

    class BookmarksForRemove():
        id = auto_field(dump_only=True, required=True)
