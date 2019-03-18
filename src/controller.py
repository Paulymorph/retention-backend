from flask import jsonify, request, abort, send_from_directory, send_file

from app import flaskApp
from models.event import Event
from models.tryFile import Try
from service import ModelHolder
from src.DataProvider import DataProvider
from src.retentioneering.utils import Config

data_provider = DataProvider()
model_settings = Config('./src/resources/settings_yaml.yaml')
model_holder = ModelHolder(data_provider, model_settings)

import os

models_folder = os.path.abspath("models")
if not os.path.exists(models_folder):
    os.makedirs(models_folder)

from flask_swagger_ui import get_swaggerui_blueprint

swagger_ui_url = '/api/docs'
swagger_api_spec_url = '/swagger.yaml'
swaggerui_blueprint = get_swaggerui_blueprint(
    swagger_ui_url,
    swagger_api_spec_url)
flaskApp.register_blueprint(swaggerui_blueprint, url_prefix=swagger_ui_url)


@flaskApp.route("/events", methods=["POST"])
def send_event():
    body = request.get_json()
    if body is None:
        abort(400, description="No body provided")
    event_try = Try(Event.init_from_json, body)
    if event_try.isSuccess:
        data_provider.add_event(event_try.result)
        return jsonify(success=True)

    else:
        abort(400, description="Exception while parsing body. %s" % event_try.exception)


@flaskApp.route("/events", methods=["GET"])
def list_events():
    events = data_provider.get_events()
    return jsonify(events=events)


@flaskApp.route("/model", methods=["GET"])
def get_model():
    model_name = request.args.get('name', type=str)
    if model_name is None:
        abort(400, description="No name of model provided")

    _ = model_holder.train_model(model_name)
    model = model_holder.get_model(model_name)

    if model is None:
        abort(400, description="No trained model with name %s" % model_name)

    model_file = "%s/%s.mlmodel" % (models_folder, model_name)
    model.to_core_ml().save(model_file)
    input_transformer = model.embedder
    embedder_vocabulary = [word for (word, index) in sorted(input_transformer.vocabulary_.items(), key=lambda i: i[1])]
    response = {
        "model": model_name,
        "transformer": {
            "type": "tf-idf",
            "idf": list(input_transformer.idf_),
            "vocabulary": embedder_vocabulary
        }
    }

    return jsonify(response)


@flaskApp.route("/model/<model_name>", methods=["GET"])
def get_saved_model(model_name):
    file_name = "%s.mlmodel" % model_name
    return send_from_directory(models_folder, file_name, attachment_filename=file_name)


@flaskApp.route("/swagger.yaml", methods=["GET"])
def swagger():
    return send_file("resources/swagger.yaml")

@flaskApp.after_request
def no_caching_header(r):
    r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    r.headers["Pragma"] = "no-cache"
    r.headers["Expires"] = "0"
    r.headers['Cache-Control'] = 'public, max-age=0'
    return r