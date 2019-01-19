import pandas as pd

from models.event import Event
from predictionModel import Model

eventsStorage = []


def loadEventExamples():
    import json
    with open("eventExamples.json") as f:
        data = json.load(f)
        events = data.get("eventExamples", [])
        for ev in events:
            addEventToStorage(Event(ev))


def eventsToDataframe(events):
    event_names = list(map(lambda x: x.eventName, events))
    event_timestamps = list(map(lambda x: x.timestamp, events))
    user_ids = list(map(lambda x: x.userId, events))
    data = {'event_name': event_names, 'event_timestamp': event_timestamps, 'user_pseudo_id': user_ids}
    df = pd.DataFrame.from_dict(data)
    return df


def addEventToStorage(event):
    eventsStorage.append(event)


class ModelHolder:

    def __init__(self):
        self.model = None

    def getModel(self):
        self.trainModel()
        return self.model

    def trainModel(self):
        if len(eventsStorage) > 10:
            print("Start training model")
            model = Model(eventsToDataframe(eventsStorage), 'leave')
            model.fit_model()
            self.model = model


modelHolder = ModelHolder()
