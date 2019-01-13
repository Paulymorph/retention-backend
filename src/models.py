from time import time

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
        self.timestamp = json.get("timestamp", int(time()))

    def serialize(self):
        return {
            "eventName": self.eventName,
            "userId": self.userId,
            "timestamp": self.timestamp
        }

    def __str__(self):
        return str(self.serialize())

    def __repr__(self):
        return self.__str__()


class CustomJSONEncoder(JSONEncoder):

    def default(self, obj):
        try:
            if isinstance(obj, Event):
                return obj.serialize()
        except TypeError as ex:
            print("Error occurred while serializing %s. %s" % (obj, ex))

        return JSONEncoder.default(self, obj)
