from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from models.custom import CustomJSONEncoder

import config

flaskApp = Flask(__name__)
flaskApp.json_encoder = CustomJSONEncoder
flaskApp.config.from_object(config)
# Disable track modifications, as it unnecessarily uses memory.
flaskApp.config.setdefault('SQLALCHEMY_TRACK_MODIFICATIONS', False)

db = SQLAlchemy()
db.init_app(flaskApp)
flaskApp.app_context().push()

import controller
