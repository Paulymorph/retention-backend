from flask.json import JSONEncoder
from app.core.model.Event import Event


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

