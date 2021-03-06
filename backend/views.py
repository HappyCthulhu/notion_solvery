import json
import os

from flask import jsonify
from flask_restful import Resource
from notifiers import get_notifier
from sqlalchemy.orm import scoped_session
from backend.tasks import test

# marshmello должен быть иницианизирован после sql_alchemy. Поэтому сначала импортим models, потом schema
from backend.models import db, NewNotionPages, BookmarksForRemove
from backend.schema import NewPagesSchema
from backend.helpers.logger_settings import logger


# TODO: подрубить серилизаторы
class AddPages(Resource):
    def __init__(self):
        self.new_pages_schema = NewPagesSchema(many=True)

    session: scoped_session = db.session
    def get(self):
        # print('test')
        # title='test'
        # link='test'
        # db.session.add(NewNotionPages(title=title, link=link))
        # new_pages = NewNotionPages.query.first()
        # print(new_pages)
        # new_pages_schema = NewPagesSchema()
        # for page in new_pages:
        #     output = new_pages_schema.jsonify(page)
        # new_pages = new_pages_schema.dump(new_pages)
        # print(new_pages)

        # db.session.commit()

        try:
            # test.s()
            new_pages = NewNotionPages.query.all()
            print(f'new_pages: {new_pages[0].title}')

            if new_pages:

                # for page in new_pages:
                #     output = new_pages_schema.jsonify(page)
                new_pages_schema = self.new_pages_schema.dump(new_pages)
                # new_pages = json.dumps([{'title': page.title, 'page_url': page.link} for page in new_pages],
                #                        ensure_ascii=False)
                print(f'new_pages_schema: {new_pages_schema}')
                logger.info(f'New pages из базы: {new_pages_schema}')

                telegram = get_notifier('telegram')
                telegram.notify(
                    message=f'New pages из базы: {new_pages}', token=os.environ['TELEGRAM_KEY'],
                    chat_id=os.environ['TELEGRAM_CHAT_ID'])

                # NewNotionPages.query.delete()
                # db.session.commit()

                telegram.notify(
                    message='В данный момент база должна быть пуста', token=os.environ['TELEGRAM_KEY'],
                    chat_id=os.environ['TELEGRAM_CHAT_ID'])
                logger.debug('В данный момент база должна быть пуста')

                return new_pages_schema

            return {}
        except Exception as e:
            return json.dumps({"error": e})

    # TODO: из JS-скрипта кидаю методы другой (delete)


class RemoveBookmarks(Resource):
    session: scoped_session = db.session
    def get(self):
        try:
            bookmarks_for_remove = BookmarksForRemove.query.all()

            if bookmarks_for_remove:
                bookmarks_for_remove = json.dumps([bookmark.bookmark_id for bookmark in bookmarks_for_remove],
                                                  ensure_ascii=False)
                print(f'bookmarks_for_remove: {bookmarks_for_remove}')
                logger.info(f'Закладки для удаления из базы: {bookmarks_for_remove}')

                telegram = get_notifier('telegram')
                telegram.notify(
                    message=f'Закладки для удаления из базы: {bookmarks_for_remove}', token=os.environ['TELEGRAM_KEY'],
                    chat_id=os.environ['TELEGRAM_CHAT_ID'])

                BookmarksForRemove.query.delete()
                db.session.commit()

                telegram.notify(
                    message='В данный момент база "bookmarks_for_remove" должна быть пуста',
                    token=os.environ['TELEGRAM_KEY'],
                    chat_id=os.environ['TELEGRAM_CHAT_ID'])
                logger.debug('В данный момент база "bookmarks_for_remove" должна быть пуста')

                return bookmarks_for_remove

            return {}
        except Exception as e:
            return json.dumps({"error": e})
