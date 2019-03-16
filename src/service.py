import logging

from PredictionModel import Model
from src.retentioneering import preparing

class ModelHolder:
    def __init__(self, data_provider, settings):
        self.model = None
        self.data_provider = data_provider
        self.settings = settings

    def get_model(self):
        self.train_model()
        return self.model

    def train_model(self):
        if self.data_provider.get_events_count > 10:
            logging.debug("Start training model")
            events = self.data_provider.get_events()
            df = self.data_provider.events_to_dataframe(events)

            logging.info('Started DataFrame shape: {}'.format(df.shape))
            df = preparing.filter_users(df, settings=self.settings)
            df = preparing.filter_events(df, settings=self.settings)
            df = preparing.drop_duplicated_events(df, settings=self.settings)
            df = preparing.add_passed_event(df, settings=self.settings)
            df = preparing.add_lost_events(df, settings=self.settings)

            logging.debug('DataFrame shape after preprocessing: {}'.format(df.shape))

            model = Model(df, 'lost')
            model.fit_model()
            self.model = model
