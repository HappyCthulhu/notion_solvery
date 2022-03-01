from celery import Celery
from backend.helpers.collect_pages_for_removing import collect_pages_for_removing

#celery -A backend.tasks worker --beat --loglevel=info

@Celery.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    # Calls test('hello') every 10 seconds.
    sender.add_periodic_task(3.0, collect_pages_for_removing(), name='add every 10')

    # Calls test('world') every 30 seconds
    # .s позволяет осуществить сторонний вызов функции test - через redis
    sender.add_periodic_task(4.0, test.s('hello world'), expires=10)

@Celery.task
def test():
    collect_pages_for_removing()

