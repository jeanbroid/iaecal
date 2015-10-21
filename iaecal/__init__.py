# __init__.py

import os

from flask import Flask
from flask.ext.babel import Babel
from flask.ext.sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config.from_object(os.environ['APP_SETTINGS'])

db = SQLAlchemy(app)
babel = Babel(app)

import iaecal.views
