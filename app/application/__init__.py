from flask import Flask
from config import CustomJSONEncoder

app = Flask(__name__)
app.json_encoder = CustomJSONEncoder

