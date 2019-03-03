from flask import jsonify, request, abort, send_from_directory, send_file

from app import flaskApp
from models.event import Event
from models.tryFile import Try
from service import ModelHolder
from src.DataProvider import DataProvider

data_provider = DataProvider()
model_holder = ModelHolder(data_provider)

import os
modelsFolder = os.path.abspath("models")
if not os.path.exists(modelsFolder):
    os.makedirs(modelsFolder)

from flask_swagger_ui import get_swaggerui_blueprint
swaggerUiUrl = '/api/docs'
swaggerApiSpecUrl = '/swagger.yaml'
swaggerui_blueprint = get_swaggerui_blueprint(
    swaggerUiUrl,
    swaggerApiSpecUrl)
flaskApp.register_blueprint(swaggerui_blueprint, url_prefix=swaggerUiUrl)


@flaskApp.route("/events", methods=["POST"])
def send_event():
    body = request.get_json()
    if body is None:
        abort(400, description="No body provided")
    event_try = Try(Event.init_from_json, body)
    if event_try.isSuccess:
        data_provider.add_event(event_try.result)
        model_holder.train_model()
        return jsonify(success=True)

    else:
        abort(400, description="Exception while parsing body. %s" % event_try.exception)


@flaskApp.route("/events", methods=["GET"])
def list_events():
    events = data_provider.get_events()
    return jsonify(events=events)


@flaskApp.route("/model/prediction", methods=["GET"])
def predict():
    model = model_holder.get_model()

    sample = request.args.get('sample', type=str)
    if sample is None:
        abort(400, "Value of `sample` is not defined.")

    prediction = model.predict_proba([sample])[0]
    return jsonify(proba=str(prediction))


@flaskApp.route("/model", methods=["GET"])
def get_model():
    model_name = "retention_model"
    model_file = "%s/%s.mlmodel" % (modelsFolder, model_name)
    model = model_holder.get_model()
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
    return send_from_directory(modelsFolder, file_name, attachment_filename=file_name)


@flaskApp.route("/swagger.yaml", methods=["GET"])
def swagger():
    return send_file("resources/swagger.yaml")
