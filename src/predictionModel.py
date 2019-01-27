import pandas as pd
from sklearn.metrics import roc_auc_score, average_precision_score, precision_recall_curve, roc_curve
from sklearn.model_selection import train_test_split
import coremltools


def str_agg(x):
    return ' '.join(x)


class Model:
    def __init__(self, data, target_event, event_filter=None,
                 n_start_events=None, emb_type='tf-idf', ngram_range=(1, 3),
                 embedder=None):
        '''
        :param data: DataFrame with columns (event_name, event_timestamp, user_pseudo_id)
        :param target_event: event_name that means the user has left
        :param event_filter: leave only the events with the names
        :param n_start_events: get only n_start_events for each user
        :param emb_type: If 'tf-idf', then _embedder will be tf-idf with ngram_range
        :param ngram_range: for tfidf if emb_type is 'tf-idf'
        :param embedder: for transformation of source df like tf-idf?
        '''
        self._source_data = data

        # data == DataFrame with columns 'event_name' and 'target'
        # data.event_name == ' '.join(one_user_event_names)
        # data.target == if data.event_name route led to target_event
        self.data = self._prepare_dataset(data, target_event, event_filter, n_start_events)
        self.features = self.data.event_name.values
        self.target = self.data.target.values
        self.users = self.data.user_pseudo_id.values
        self.emb_type = emb_type
        self.embedder = embedder
        self.ngram_range = ngram_range
        self.roc_auc_score = None
        self.average_precision_score = None
        self.roc_c = None
        self.prec_rec = None

        if embedder:
            self._fit_vec = False
        else:
            self._fit_vec = True

    def _get_vectors(self, sample):
        if self._fit_vec:
            self._fit_vectors(sample)
        return self.embedder.transform(sample)

    def _fit_vectors(self, sample):
        if self.emb_type == 'tf-idf':
            from sklearn.feature_extraction.text import TfidfVectorizer
            tfidf = TfidfVectorizer(ngram_range=self.ngram_range)
            self.embedder = tfidf.fit(sample)
            self._fit_vec = False

    def _prepare_dataset(self, df, target_event, event_filter=None, n_start_events=None):
        if event_filter is not None:
            df = df[df.event_name.isin(event_filter)]
        df = df.sort_values('event_timestamp')
        train = df.groupby('user_pseudo_id').event_name.agg(str_agg)
        train = train.reset_index(None)
        train.event_name = train.event_name.apply(lambda x: x.split())
        train['target'] = train.event_name.apply(lambda x: x[-1] == target_event)
        train.event_name = train.event_name.apply(lambda x: x[:-1])
        if n_start_events:
            train.event_name = train.event_name.apply(lambda x: ' '.join(x[:n_start_events]))
        else:
            train.event_name = train.event_name.apply(lambda x: ' '.join(x))
        return train

    def _prepare_data(self):
        x_train, x_test, y_train, y_test = train_test_split(self.features, self.target, test_size=0.2, random_state=42)
        x_train_vec = self._get_vectors(x_train)
        x_test_vec = self._get_vectors(x_test)
        return x_train_vec, x_test_vec, y_train, y_test

    def _validate(self, x_test_vec, y_test):
        preds = self.model.predict_proba(x_test_vec)
        self.roc_auc_score = roc_auc_score(y_test, preds[:, 1])
        self.average_precision_score = average_precision_score(y_test, preds[:, 1])
        print('ROC-AUC: {:.4f}'.format(self.roc_auc_score))
        print('PR-AUC: {:.4f}'.format(self.average_precision_score))
        self.roc_c = roc_curve(y_test, preds[:, 1])
        self.prec_rec = precision_recall_curve(y_test, preds[:, 1])

    def fit_model(self, model_type='logit'):
        self.model_type = model_type
        x_train_vec, x_test_vec, y_train, y_test = self._prepare_data()
        if model_type == 'logit':
            from sklearn.linear_model import LogisticRegression
            lr = LogisticRegression(penalty='l1')
            lr.fit(x_train_vec, y_train)
            self.model = lr
        # self._validate(x_test_vec, y_test)

    def predict_proba(self, sample):
        vec = self._get_vectors(sample)
        return self.model.predict_proba(vec)

    def build_important_track(self):
        if self.model_type == 'logit':
            imp = self.model.coef_
        if self.emb_type == 'tf-idf':
            imp = self.embedder.inverse_transform(imp)[0]
        edges = []
        for i in imp:
            j = i.split()
            if len(j) == 2:
                edges.append(j)
            elif len(j) > 2:
                for k in range(1, len(j)):
                    edges.append([j[k - 1], j[k]])
            elif len(j) == 1:
                edges.append([j[0], None])
        return pd.DataFrame(edges).drop_duplicates()

    def to_core_ml(self):
        return coremltools.converters.sklearn.convert(self.model)
