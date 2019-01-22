from flask import jsonify, request, abort

from app import flaskApp
from models.event import Event
from models.tryFile import Try
from service import addEventToStorage, eventsStorage, modelHolder, loadEventExamples


@flaskApp.before_first_request
def preLoad():
    loadEventExamples()


@flaskApp.route("/events", methods=["POST"])
def sendEvent():
    body = request.get_json()
    if body is None:
        abort(400, description="No body provided")
    eventTry = Try(Event, body)
    if eventTry.isSuccess:
        addEventToStorage(eventTry.result)
        modelHolder.trainModel()
        return jsonify(success=True)

    else:
        abort(400, description="Exception while parsing body. %s" % eventTry.exception)


@flaskApp.route("/events", methods=["GET"])
def listEvents():
    return jsonify(events=eventsStorage)


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
    coreMlModel = modelHolder.getModel().to_core_ml()
    spec = coreMlModel.get_spec()
    serialized = spec.SerializeToString()
    return serialized
