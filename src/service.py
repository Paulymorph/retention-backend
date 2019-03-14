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

            # add passed events from settings['positive_event']
            df = preparing.add_passed_event(df, settings=self.settings)
            logging.debug('DataFrame shape after adding passed events: {}'.format(df.shape))

            # add lost events from settings['negative_event']
            df = preparing.add_lost_events(df, settings=self.settings)
            logging.debug('DataFrame shape after adding lost events: {}'.format(df.shape))

            model = Model(df, 'lost')
            model.fit_model()
            self.model = model
