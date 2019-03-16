import pandas as pd
from sqlalchemy import MetaData, Table, Column, String, DateTime

from src.app import db
from src.models.event import Event


class DataProvider:
    def __init__(self):
        self._engine = db.engine
        self._meta = MetaData(self._engine)
        self._event_table = Table('events', self._meta,
                                  Column('event_name', String),
                                  Column('event_time', DateTime),
                                  Column('user_id', String))

    @staticmethod
    def events_to_dataframe(events):
        event_names = list(map(lambda x: x.eventName, events))
        event_timestamps = list(map(lambda x: x.timestamp, events))
        user_ids = list(map(lambda x: x.userId, events))
        data = {'event_name': event_names, 'event_timestamp': event_timestamps, 'user_pseudo_id': user_ids}
        df = pd.DataFrame.from_dict(data)
        return df

    def add_event(self, event):
        if type(event) is list:
            statement = self._event_table.insert()
            keys_map = {'eventName': 'event_name', 'timestamp': 'event_time', 'userId': 'user_id'}

            def to_database(event):
                event_dict = event.__dict__
                return {keys_map[old_key]: value for old_key, value in event_dict.items()}

            events = list(map(to_database, event))
            self._engine.execute(statement, events)
        else:
            statement = self._event_table.insert().values(event_name=event.eventName, event_time=event.timestamp, user_id=event.userId)
            self._engine.execute(statement)

    def get_events(self):
        statement = self._event_table.select()
        results = self._engine.execute(statement)
        return list(map(lambda q: Event.init_from_query(q), results))

    def get_events_count(self):
        statement = self._event_table.count()
        res = self._engine.execute(statement)
        return next(res)[0]