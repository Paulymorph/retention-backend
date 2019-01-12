from time import time

from flask import Flask, request, abort, jsonify
from flask.json import JSONEncoder


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


@app.route("/sendEvent", methods=["POST"])
def sendEvent():
    body = request.get_json()
    if body is None:
        abort(400, description="No body provided")
    eventTry = Try(Event, body)
    if eventTry.isSuccess:
        addEventToStorage(eventTry.result)
        return jsonify(success=True)

    else:
        abort(400, description="Exception while parsing body. %s" % eventTry.exception)


@app.route("/events", methods=["GET"])
def listEvents():
    return jsonify(events=list(eventsStorage))


eventsStorage = []


def addEventToStorage(event):
    eventsStorage.append(event)
