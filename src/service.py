import pandas as pd
from sqlalchemy import MetaData, Table, Column, Integer, select, func

from src.app import db
from models.event import Event
from predictionModel import Model

engine = db.engine
meta = MetaData(engine)

event_table = Table('events', meta,
                    Column('event_name', Integer),
                    Column('event_time', Integer),
                    Column('user_id', Integer))
# eventsStorage = []


# def loadEventExamples():
#     import json
#     with open("eventExamples.json") as f:
#         data = json.load(f)
#         events = data.get("eventExamples", [])
#         for ev in events:
#             add_event_to_storage(Event(ev))


def eventsToDataframe(events):
    event_names = list(map(lambda x: x.eventName, events))
    event_timestamps = list(map(lambda x: x.timestamp, events))
    user_ids = list(map(lambda x: x.userId, events))
    data = {'event_name': event_names, 'event_timestamp': event_timestamps, 'user_pseudo_id': user_ids}
    df = pd.DataFrame.from_dict(data)
    return df


def add_event_to_storage(event):
    statement = event_table.insert().values(event_name=event.eventName, event_time=event.timestamp, user_id=event.userId)
    engine.execute(statement)


# Get all events from database
def get_events_from_storage():
    statement = event_table.select()
    results = engine.execute(statement)
    return list(map(lambda q: Event.init_from_query(q), results))


# Get total events count
def get_events_count():
    statement = event_table.count()
    res = engine.execute(statement)
    return next(res)[0]


class ModelHolder:

    def __init__(self):
        self.model = None

    def getModel(self):
        self.trainModel()
        return self.model

    def trainModel(self):
        if get_events_count() > 10:
            print("Start training model")
            events = get_events_from_storage()
            model = Model(eventsToDataframe(events), 'leave')
            model.fit_model()
            self.model = model


modelHolder = ModelHolder()
