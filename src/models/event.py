from time import time


class Event(object):

    def __init__(self, event_name, timestamp, user_id):
        self.eventName = event_name
        self.userId = user_id
        self.timestamp = timestamp

    @classmethod
    def init_from_json(cls, json):
        return cls(json["eventName"], json["userId"], json.get("timestamp", int(time())))

    @classmethod
    def init_from_query(cls, query):
        return cls(query[0], query[1], query[2])

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
