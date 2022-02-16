import os
import signal
import sys

from flask import Flask
from flask_apscheduler import APScheduler


# from backend.helpers.collect_pages_for_removing import collect_pages_for_removing
# from backend.helpers.notion_tracking import notion_tracking

from backend.helpers.logger_settings import logger
from flask_cors import CORS


if os.environ['APP_SETTINGS'] == 'Development':
    from config import DevelopmentConfig as Config

elif os.environ['APP_SETTINGS'] == 'Production':
    from config import Config





app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = Config.SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# preventing error "been blocked by CORS policy: No 'Access-Control-Allow-Origin' header is present on the requested resource"
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'




# def signal_handler(signal, frame):
#     db.session.close()
#     logger.info('DB connection was closed')
#     sys.exit(0)


# print('Запускаем шедулеры')
# signal.signal(signal.SIGINT, signal_handler)


# scheduler = APScheduler()
#
# scheduler.add_job(id='notion_tracking task', func=notion_tracking, trigger='interval', seconds=200)
# scheduler.add_job(id='collect_pages_for_removing task', func=collect_pages_for_removing, trigger='interval',
#                   seconds=10)
# scheduler.start()


app.run(host='0.0.0.0')