from flask import Flask

from models.custom import CustomJSONEncoder

flaskApp = Flask(__name__)
flaskApp.json_encoder = CustomJSONEncoder

import controller
