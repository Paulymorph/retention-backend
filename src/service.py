import logging

import DataProvider
from PredictionModel import Model
from retentioneering.utils import Config
from src.retentioneering import preparing


class ModelHolder:
    def __init__(self, data_provider, settings):
        # type: (DataProvider, Config) -> None
        self.data_provider = data_provider
        self.settings = settings
        self.models_container = dict()

    def get_model(self, name):
        return self.models_container.get(name)

    def train_model(self, name):
        """
        At this moment `name` bound to the group of "positive events" defined in config (i.e. "settings_yaml.yaml").
        But in future implementation the naming principle could be changed.
        :param name: Name of model to train
        :return:
        """
        if self.data_provider.get_events_count > 10:
            logging.debug("Start training model")
            events = self.data_provider.get_events()
            df = self.data_provider.events_to_dataframe(events)

            logging.info('Started parsing configs: {}'.format(df.shape))

            local_settings = dict() if self.settings is None else self.settings  # type: Dict[str, Any]
            users_filters = local_settings.get('users', {}).get('filters', [])
            events_filters = local_settings.get('events', {}).get('filters', [])
            duplicate_thr_time = local_settings.get('events', {}).get('duplicate_thr_time', 0)
            positive_event_name = local_settings.get('positive_event', {}).get('name', u'passed')
            positive_event_filter = local_settings.get('positive_event', {}).get('filters', {}).get(name, None)
            if positive_event_filter is None:
                return
            negative_event_name = local_settings.get('negative_event', {}).get('name', u'lost')

            logging.info('Started DataFrame shape: {}'.format(df.shape))

            df = preparing.filter_users(df, users_filters)
            df = preparing.filter_events(df, events_filters)
            df = preparing.drop_duplicated_events(df, duplicate_thr_time)
            df = preparing.add_passed_event(df, positive_event_name, positive_event_filter)
            df = preparing.add_lost_events(df, positive_event_name, negative_event_name)

            logging.debug('DataFrame shape after preprocessing: {}'.format(df.shape))

            model = Model(df, negative_event_name)
            model.fit_model()
            self.models_container[name] = model
