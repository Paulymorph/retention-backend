from flask import jsonify, request, abort, send_from_directory, send_file

from app import flaskApp
from models.event import Event
from models.tryFile import Try
from service import add_event_to_storage, modelHolder, get_events_from_storage

import os

modelsFolder = os.path.abspath("models")

from flask_swagger_ui import get_swaggerui_blueprint
swaggerUiUrl = '/api/docs'
swaggerApiSpecUrl = '/swagger.yaml'
swaggerui_blueprint = get_swaggerui_blueprint(
    swaggerUiUrl,
    swaggerApiSpecUrl)
flaskApp.register_blueprint(swaggerui_blueprint, url_prefix=swaggerUiUrl)

# @flaskApp.before_first_request
# def preLoad():
#     if not os.path.exists(modelsFolder):
#         os.makedirs(modelsFolder)
#     loadEventExamples()


@flaskApp.route("/events", methods=["POST"])
def sendEvent():
    body = request.get_json()
    if body is None:
        abort(400, description="No body provided")
    eventTry = Try(Event.init_from_json, body)
    if eventTry.isSuccess:
        add_event_to_storage(eventTry.result)
        modelHolder.trainModel()
        return jsonify(success=True)

    else:
        abort(400, description="Exception while parsing body. %s" % eventTry.exception)


@flaskApp.route("/events", methods=["GET"])
def listEvents():
    events = get_events_from_storage()
    return jsonify(events=events)


@flaskApp.route("/model/prediction", methods=["GET"])
def predict():
    model = modelHolder.getModel()

    sample = request.args.get('sample', type=str)
    if sample is None:
        abort(400, "Value of `sample` is not defined.")

    prediction = model.predict_proba([sample])[0]
    return jsonify(proba=str(prediction))


@flaskApp.route("/model", methods=["GET"])
def getModel():
    modelName = "retention_model"
    modelFile = "%s/%s.mlmodel" % (modelsFolder, modelName)
    model = modelHolder.getModel()
    model.to_core_ml().save(modelFile)
    inputTransformer = model.embedder
    embedderVocabulary = [word for (word, index) in sorted(inputTransformer.vocabulary_.items(), key = lambda i: i[1])]
    response = {
        "model": modelName,
        "transformer": {
            "type": "tf-idf",
            "idf": list(inputTransformer.idf_),
            "vocabulary": embedderVocabulary
        }
    }

    return jsonify(response)


@flaskApp.route("/model/<modelName>", methods=["GET"])
def getSavedModel(modelName):
    fileName = "%s.mlmodel" % modelName
    return send_from_directory(modelsFolder, fileName, attachment_filename = fileName)


@flaskApp.route("/swagger.yaml", methods=["GET"])
def swagger():
    return send_file("resources/swagger.yaml")
