from application import app

from flask import request, abort, jsonify
from core.model.Event import Event
from core.model.Model import Model
import pandas as pd


class Try:

    def __init__(self, func, *args):
        try:
            self.result = func(*args)
            self.isSuccess = True
        except Exception as ex:
            self.exception = ex
            self.isSuccess = False


class ParseBodyException(ValueError):
    pass


# @app.before_first_request
# def preLoad():
#     loadEventExamples()

@app.route("/events", methods=["POST"])
def sendEvent():
    body = request.get_json()
    if body is None:
        abort(400, description="No body provided")
    eventTry = Try(Event, body)
    if eventTry.isSuccess:
        addEventToStorage(eventTry.result)
        fit_model()
        return jsonify(success=True)

    else:
        abort(400, description="Exception while parsing body. %s" % eventTry.exception)


def fit_model():
    if len(eventsStorage) > 10:
        modelHodler.model = Model(events_to_dataframe(eventsStorage), 'leave')
        modelHodler.model.fit_model()


@app.route("/events", methods=["GET"])
def listEvents():
    return jsonify(events=list(eventsStorage))


eventsStorage = [Event({'eventName': u'assdf', 'timestamp': 1547396627, 'userId': 1}),
                 Event({'eventName': u'assdf', 'timestamp': 1547396630, 'userId': 1}),
                 Event({'eventName': u'aseerf', 'timestamp': 1547396633, 'userId': 1}),
                 Event({'eventName': u'asdfsdfsdf', 'timestamp': 1547396635, 'userId': 1}),
                 Event({'eventName': u'assdf', 'timestamp': 1547396640, 'userId': 1}),
                 Event({'eventName': u'asdfsdfsdf', 'timestamp': 1547396644, 'userId': 1}),
                 Event({'eventName': u'asdfsdfsdf', 'timestamp': 1547396647, 'userId': 1}),
                 Event({'eventName': u'asdfsdfsdf', 'timestamp': 1547396648, 'userId': 1}),
                 Event({'eventName': u'assdf', 'timestamp': 1547396653, 'userId': 1}),
                 Event({'eventName': u'asdfsdfsdf', 'timestamp': 1547396655, 'userId': 1}),
                 Event({'eventName': u'asdfsdfsdf', 'timestamp': 1547396656, 'userId': 1}),
                 Event({'eventName': u'leave', 'timestamp': 1547396756, 'userId': 1}),
                 Event({'eventName': u'asdfsdfsdf', 'timestamp': 1547396822, 'userId': 0}),
                 Event({'eventName': u'asdfsdfsdf', 'timestamp': 1547396841, 'userId': 3}),
                 Event({'eventName': u'asdfsdfsdf', 'timestamp': 1547396851, 'userId': 5}),
                 Event({'eventName': u'leave', 'timestamp': 1547397004, 'userId': 5}),
                 Event({'eventName': u'leaves', 'timestamp': 1547397073, 'userId': 5}),
                 Event({'eventName': u'leave', 'timestamp': 1547397268, 'userId': 2}),
                 Event({'eventName': u'leave', 'timestamp': 1547397462, 'userId': 2}),
                 Event({'eventName': u'leave', 'timestamp': 1547397589, 'userId': 5}),
                 Event({'eventName': u'leave', 'timestamp': 1547397649, 'userId': 5})]


class ModelHolder:

    def __init__(self):
        self.model = None

    def getModel(self):
        self.trainModel()
        return self.model

    def trainModel(self):
        if len(eventsStorage) > 10:
            print("Start training model")
            model = Model(events_to_dataframe(eventsStorage), 'leave')
            model.fit_model()
            self.model = model


modelHolder = ModelHolder()

modelHodler = ModelHolder()


def events_to_dataframe(events):
    event_names = list(map(lambda x: x.eventName, events))
    event_timestamps = list(map(lambda x: x.timestamp, events))
    user_ids = list(map(lambda x: x.userId, events))
    data = {'event_name': event_names, 'event_timestamp': event_timestamps, 'user_pseudo_id': user_ids}
    return pd.DataFrame.from_dict(data)


def addEventToStorage(event):
    eventsStorage.append(event)


@app.route("/model/prediction", methods=["GET"])
def predict():
    model = modelHodler.getModel()

    sample = request.args.get('sample', type=str)
    if sample is None:
        abort(400, "Value of `sample` is not defined.")

    prediction = model.predict_proba([sample])[0]
    return jsonify(proba=str(prediction))


@app.route("/getModel", methods=["GET"])
def getModel():
    coreMlModel = modelHodler.getModel().to_core_ml()
    return jsonify(coreMlModel)
