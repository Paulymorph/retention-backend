from flask import Flask
from application.config import CustomJSONEncoder

app = Flask(__name__)
app.json_encoder = CustomJSONEncoder

from application import controller
