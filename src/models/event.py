from time import time


class Event(object):

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
