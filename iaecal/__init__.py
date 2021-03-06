# __init__.py

import os

from flask import Flask
from flask.ext.assets import Environment
from flask.ext.babel import Babel
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.seasurf import SeaSurf

from iaecal.serializers import JSONEncoder


assets = Environment()
babel = Babel()
db = SQLAlchemy()
csrf = SeaSurf()


def create_app(config_object=os.environ['APP_SETTINGS']):
    app = Flask(__name__)
    app.config.from_object(config_object)

    assets.init_app(app)
    babel.init_app(app)
    db.init_app(app)
    csrf.init_app(app)

    # Register blueprints
    from iaecal.views import bp
    app.register_blueprint(bp)

    with app.app_context():
        db.create_all()

    # Set up logging
    setup_logging(app)

    # Set a specific json encoder
    app.json_encoder = JSONEncoder

    return app


def setup_logging(app):
    if app.debug:
        return

    import logging
    from logging.handlers import SMTPHandler
    from logging import StreamHandler

    # Configure mail logging for error and critical messages
    mail_handler = SMTPHandler(
        (app.config['MAIL_SERVER'], app.config['MAIL_PORT']),
        app.config['MAIL_DEFAULT_SENDER'],
        app.config['MAIL_ADMINS'],
        'IAECal Failed',
        credentials=(app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD']),
    )
    mail_handler.setLevel(logging.ERROR)
    base_dir = os.path.dirname(os.path.realpath(__file__))
    with open(os.path.join(base_dir, 'mail_handler_format.txt')) as f:
        mail_handler.setFormatter(logging.Formatter(f.read()))

    # Configure stderr logging for warning messages
    stream_handler = StreamHandler()
    stream_handler.setLevel(logging.WARNING)
    stream_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s '
        '[in %(pathname)s:%(lineno)d]'
    ))

    # Configure logging for apps and libraries
    loggers = [app.logger, logging.getLogger('sqlalchemy')]
    for logger in loggers:
        logger.addHandler(mail_handler)
        logger.addHandler(stream_handler)
