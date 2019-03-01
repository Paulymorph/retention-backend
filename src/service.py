from predictionModel import Model


class ModelHolder:
    def __init__(self, data_provider):
        self.model = None
        self.data_provider = data_provider

    def get_model(self):
        self.train_model()
        return self.model

    def train_model(self):
        if len(self.data_provider.get_events_count) > 10:
            print("Start training model")
            events = self.data_provider.get_events()
            model = Model(self.data_provider.eventsToDataframe(events), 'leave')
            model.fit_model()
            self.model = model
