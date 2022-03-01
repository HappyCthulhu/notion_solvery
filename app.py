import os
import signal
import sys

from make_celery import make_celery
from flask import Flask
from flask_cors import CORS

from backend.helpers.logger_settings import logger
from backend.models import db
from backend.urls import api_bp

if os.environ['APP_SETTINGS'] == 'Development':
    from config import DevelopmentConfig as Config

elif os.environ['APP_SETTINGS'] == 'Production':
    from config import Config


# TODO: config_filename? wtf

def create_app(config_filename):
    app = Flask(__name__)
    app.config.from_object(config_filename)

    app.register_blueprint(api_bp, url_prefix='/')
    app.config['SQLALCHEMY_DATABASE_URI'] = Config.SQLALCHEMY_DATABASE_URI
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    from backend.schema import ma
    ma.init_app(app)


    # preventing error "been blocked by CORS policy: No 'Access-Control-Allow-Origin' header is present on the requested resource"
    cors = CORS(app)
    app.config['CORS_HEADERS'] = 'Content-Type'
    return app


def signal_handler(signal, frame):
    db.session.close()
    logger.info('DB connection was closed')
    sys.exit(0)



app = create_app("config")
# app.app_context().push()
celery = make_celery(app)
signal.signal(signal.SIGINT, signal_handler)


if __name__ == "__main__":
    app.run(debug=True)
