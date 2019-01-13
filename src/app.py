from flask import jsonify, request, abort, Flask

from models import Event, Try, CustomJSONEncoder
from service import addEventToStorage, eventsStorage, loadEventExamples, modelHolder

loadEventExamples()
flaskApp = Flask(__name__)
flaskApp.json_encoder = CustomJSONEncoder


@flaskApp.route("/events", methods=["POST"])
def sendEvent():
    body = request.get_json()
    if body is None:
        abort(400, description="No body provided")
    eventTry = Try(Event, body)
    if eventTry.isSuccess:
        addEventToStorage(eventTry.result)
        modelHolder.fit_model()
        return jsonify(success=True)

    else:
        abort(400, description="Exception while parsing body. %s" % eventTry.exception)


@flaskApp.route("/events", methods=["GET"])
def listEvents():
    return jsonify(events=list(eventsStorage))


@flaskApp.route("/model/prediction", methods=["GET"])
def predict():
    model = modelHolder.getModel()

    sample = request.args.get('sample', type=str)
    if sample is None:
        abort(400, "Value of `sample` is not defined.")

    prediction = model.predict_proba([sample])[0]
    return jsonify(proba=str(prediction))
