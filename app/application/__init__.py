from flask import Flask
from app.application.config import CustomJSONEncoder

app = Flask(__name__)
app.json_encoder = CustomJSONEncoder

