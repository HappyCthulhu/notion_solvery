import os
import sys
from datetime import datetime

import psycopg2 as psycopg2
from notifiers import get_notifier
from notion.block import PageBlock
from notion.client import NotionClient
from requests.exceptions import HTTPError
from sqlalchemy import and_

from backend.models import db, NewNotionPages, AllNotionPages
from .logger_settings import logger


def timestamp_to_datetime(timestamp):
    return datetime.fromtimestamp(float(str(timestamp)[0:-3]))


def get_conn_and_cursor():
    conn = psycopg2.connect(host=os.environ['DB_HOST_NAME'], user=os.environ['DB_USER_NAME'],
                            password=os.environ['DB_PASSWORD'], dbname=os.environ['DB_NAME'])
    cursor = conn.cursor()
    return conn, cursor


def get_childs(page):
    children_pages = page.children.filter(type=PageBlock)
    return children_pages


def compare_depth_to_length(depth):
    if len(path[-1]['title'].split("/")) < depth + 1:
        return 'depth_more_than_length'

    elif len(path[-1]['title'].split("/")) == depth + 1:
        return 'length_and_depth_are_equal'

    else:
        return 'length_more_than_depth'


def append_in_list(var, title, url):
    var.append({'title': title, 'url': url})


def create_bookmark_data(comparing_depth_to_length, depth, _block):
    _dict = {
        'depth_more_than_length': (f'{path[-1]["title"]}/{_block.title.lower()}', _block.get_browseable_url()),
        'length_and_depth_are_equal': (
            f"{'/'.join(path[-1]['title'].split('/')[0:-1])}/{_block.title.lower()}", _block.get_browseable_url()),
        'length_more_than_depth': (
            f"{'/'.join(path[-1]['title'].split('/')[0:depth])}/{_block.title.lower()}", _block.get_browseable_url())
    }

    bookmark = _dict[comparing_depth_to_length]

    return bookmark


def collect_pages(block, depth=0):
    if depth == 0:
        path.append({'title': block.title.lower(), 'page_url': block.get_browseable_url(),
                     'created_time': timestamp_to_datetime(block._get_record_data()['created_time']),
                     'last_edited_time': timestamp_to_datetime(block._get_record_data()['last_edited_time'])})

    else:
        comparing_depth_to_length = compare_depth_to_length(depth)
        page_name, page_url = create_bookmark_data(comparing_depth_to_length, depth, block)

        path.append({'title': page_name, 'page_url': page_url,
                     'created_time': timestamp_to_datetime(block._get_record_data()['created_time']),
                     'last_edited_time': timestamp_to_datetime(block._get_record_data()['last_edited_time'])})

    for child in block.children:
        if child.type in ["page", "collection"]:
            collect_pages(child, depth=depth + 1)


def not_changed_page(current_page):
    first_founded_page = db.session.query(AllNotionPages).filter(
        and_(AllNotionPages.link == current_page['page_url'],
             AllNotionPages.title == current_page['title'])).first()

    if first_founded_page:
        first_founded_page.last_edited_time = current_page['last_edited_time']
        db.session.commit()
        return True


def new_page(current_page):
    exist_in_db = db.session.query(AllNotionPages).filter(
        and_(AllNotionPages.link == current_page['page_url'], AllNotionPages.title == current_page['title'])).all()

    if not exist_in_db:
        title = current_page['title']
        link = current_page['page_url']
        created_time = current_page['created_time']
        last_edited_time = current_page['last_edited_time']

        telegram.notify(
            message=current_page['title'], token=os.environ['TELEGRAM_KEY'], chat_id=os.environ['TELEGRAM_CHAT_ID'])

        db.session.add(NewNotionPages(title=title, link=link, created_time=created_time,
                                      last_edited_time=last_edited_time))

        db.session.add(AllNotionPages(title=title, link=link, created_time=created_time,
                                      last_edited_time=last_edited_time))
        db.session.commit()
        return True


def renamed_page(current_page):
    renamed_page = db.session.query(AllNotionPages).filter(and_(AllNotionPages.link == current_page['page_url'],
                                                                AllNotionPages.title != current_page[
                                                                    'title'])).all()

    if renamed_page:
        renamed_page = db.session.query(AllNotionPages).filter(and_(AllNotionPages.link == current_page['page_url'],
                                                                    AllNotionPages.title != current_page[
                                                                        'title'])).first()
        # this commit is needed, because link column consist unique values (script will try 2 push non-uniq value of renamed page without this commit)
        renamed_page.last_edited_time = current_page['last_edited_time']
        # TODO: здесь нужно created_time?
        renamed_page.title = current_page['title']
        db.session.commit()
        return True


def process_existing_in_notion_pages(path):
    for current_page in path:
        if not_changed_page(current_page):
            continue
        # important order: first - renamed_page func, than new_page
        elif renamed_page(current_page):
            continue
        elif new_page(current_page):
            continue
        else:
            logger.critical('Some weird shit happend. But u will find out very quick, i promise!')
            sys.exit()


def delete_in_db_deleted_notion_pages(all_current_pages):
    # в БД есть запись с таким же url, но другим названием: удаляем из БД, добавляем новую запись
    # БД содержит название и url заметки, которой нет в Notion: удаляем из БД
    current_pages_links = [page_from_db['page_url'] for page_from_db in all_current_pages]
    old_pages_links = [page.link for page in db.session.query(AllNotionPages).all()]
    for old_link in old_pages_links:

        # БД содержит url заметки, котоой нет в notion
        if old_link not in current_pages_links:
            logger.debug(f'Найдена запись в all_notion_pages, url которой нет Notion. Удаляю из БД: {old_link}')
            db.session.query(AllNotionPages).filter(AllNotionPages.link == old_link).delete()
            db.session.commit()


def notion_tracking():
    logger.debug('Start tracking Notion')

    try:
        client = NotionClient(token_v2=os.environ.get('TOKEN'))

    except HTTPError:
        logger.critical('Wrong notion token')
        sys.exit()

    link = os.environ['LINK']
    page = client.get_block(link)
    child_pages = get_childs(page)

    global path
    path = []

    for block in child_pages:
        collect_pages(block)

    delete_in_db_deleted_notion_pages(path)
    process_existing_in_notion_pages(path)
    logger.debug('Finished tracking Notion')


# TODO: не стоит ли подтягивать в ДБ all_notion_pages те страницы, что были найдены в дб new_pages? А то сейчас это иначе происходит
telegram = get_notifier('telegram')
# TODO: мб стоит прихуярить логгирование к переименованным и удаленным страницам? Разве это не сделано?
# TODO: проверяю ли я где-то перед добавлянием новой страницы в букмарки, нет ли ее в букмарках случаем?
# TODO: сделать интеграционный тест для дублирования закладок. Пока непонятно, как. Это ж нужно через сервак делать
