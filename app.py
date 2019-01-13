from time import time

from flask import Flask, request, abort, jsonify
from flask.json import JSONEncoder
from model.Model import Model
import pandas as pd


class Try:

    def __init__(self, func, *args):
        try:
            self.result = func(*args)
            self.isSuccess = True
        except Exception as ex:
            self.exception = ex
            self.isSuccess = False


class Event:

    def __init__(self, json):
        self.eventName = json["eventName"]
        self.userId = json["userId"]
        self.timestamp = int(time())


class CustomJSONEncoder(JSONEncoder):

    def serializeEvent(self, event):
        return {
            "eventName": event.eventName,
            "userId": event.userId,
            "timestamp": event.timestamp
        }

    def default(self, obj):
        try:
            if isinstance(obj, Event):
                return self.serializeEvent(obj)
        except TypeError as ex:
            print("Error occurred while serializing %s. %s" % (obj, ex))

        return JSONEncoder.default(self, obj)


class ParseBodyException(ValueError):
    pass


app = Flask(__name__)
app.json_encoder = CustomJSONEncoder


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
    model = modelHodler.model

    if model is None:
        fit_model()
        abort(400, description="The model is untrained yet")
    else:
        sample = request.args.get('sample', type=str)
        prediction = model.predict_proba([sample])[0]
        return jsonify(proba=str(prediction))

