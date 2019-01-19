from time import time


class Event:

    def __init__(self, json):
        self.eventName = json["eventName"]
        self.userId = json["userId"]
        self.timestamp = int(time())
