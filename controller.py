from flask import Flask, request, abort, jsonify
from flask.json import JSONEncoder

voidType = type(None)


def log(msg: str) -> voidType:
    print(msg)


class Try:

    def __init__(self, func, *args) -> voidType:
        try:
            self.result = func(*args)
            self.isSuccess = True
        except Exception as ex:
            self.exception = ex
            self.isSuccess = False


class Event:

    def __init__(self, json):
        self.sessionId = json["sessionId"]
        self.screen = json["screen"]
        self.element = json["element"]
        self.eventId = json["eventId"]
        self.userId = json["userId"]


class CustomJSONEncoder(JSONEncoder):

    def serializeEvent(self, event: Event):
        return {
            "sessionId": event.sessionId,
            "screen": event.screen,
            "element": event.element,
            "eventId": event.eventId,
            "userId": event.userId,
        }

    def default(self, obj):
        try:
            if isinstance(obj, Event):
                return self.serializeEvent(obj)
        except TypeError as ex:
            print(f"Error occurred while serializing {obj}. {ex}")

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
        abort(400, description=f"Exception while parsing body. {eventTry.exception}")


@app.route("/events", methods=["GET"])
def listEvents():
    return jsonify(events=list(eventsStorage.values()))


eventsStorage = dict()


def addEventToStorage(event: Event) -> voidType:
    eventsStorage[event.eventId] = event
