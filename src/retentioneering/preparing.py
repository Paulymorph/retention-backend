import logging

import pandas as pd


def drop_duplicated_events(df, duplicate_thr_time):
    """
    Delete duplicated events (two events with save event names if the time between them less than duplicate_thr_time).

    :param df: input pd.DataFrame
    :param duplicate_thr_time: threshold for time between events

    :type df: pd.DataFrame
    :type duplicate_thr_time: int
    :return: self
    :rtype: pd.DataFrame
    """
    logging.info('Start. Shape: {}'.format(df.shape))
    df = df.sort_values(['user_pseudo_id', 'event_timestamp'])
    is_first_iter = 1
    duplicated_rows = None

    while is_first_iter or duplicated_rows.sum() != 0:
        if is_first_iter != 1:
            df = df.loc[~duplicated_rows, :]
        is_first_iter = 0
        df.loc[:, 'prev_timestamp'] = df.event_timestamp.shift(1)
        df.loc[:, 'prev_user'] = df.user_pseudo_id.shift(1)
        df.loc[:, 'prev_event_name'] = df.event_name.shift(1)

        duplicated_rows = (((df.event_timestamp - df.prev_timestamp).map(lambda x: x.seconds) <= duplicate_thr_time) &
                           (df.prev_event_name == df.event_name) &
                           (df.prev_user == df.user_pseudo_id))
    logging.info('Done. Shape: {}'.format(df.shape))
    df = df.drop(['prev_timestamp', 'prev_user', 'prev_event_name'], axis=1)
    return df


def filter_users(df, filters):
    """
    Apply filters to users from the input table and leave all events for the received users.

    :param df: input pd.DataFrame
    :param filters: list each element of which is a filter dict

    :type df: pd.DataFrame
    :type filters: list
    :return: pd.DataFrame
    """
    logging.info('Start. Shape: {}'.format(df.shape))
    conditions = _filter_conditions(df, filters)
    if conditions is not None:
        df = df.loc[df.user_pseudo_id.isin(df.loc[conditions, 'user_pseudo_id']), :].copy()
    logging.info('Done. Shape: {}'.format(df.shape))
    return df


def filter_events(df, filters):
    """
    Apply filters to the input table.

    :param df: input pd.DataFrame
    :param filters: list each element of which is a filter dict

    :type df: pd.DataFrame
    :type filters: list
    :return: self
    :rtype: pd.DataFrame
    """
    logging.info('Start. Shape: {}'.format(df.shape))
    conditions = _filter_conditions(df, filters)
    if conditions is not None:
        df = df.loc[conditions, :].copy()
    logging.info('Done. Shape: {}'.format(df.shape))
    return df


def _filter_conditions(df, filters):
    if len(filters) == 0:
        return None
    conditions = False
    for i, one_filter in enumerate(filters):
        event_name = one_filter.get('event_name')
        event_value = one_filter.get('event_params_value_string_value')
        is_not = one_filter.get('not', False)
        condition = True
        if event_name:
            condition &= (df.event_name == event_name)
        if event_value:
            condition &= (df.event_params_value_string_value == event_value)
        if is_not:
            condition = ~condition
        conditions |= condition
    return conditions


def add_passed_event(df, positive_event_name, filters):
    # type: (pd.DataFrame, str, dict) -> pd.DataFrame
    """
    Add new events with `positive_event_name` and delete all events after.

    :param df: input pd.DataFrame
    :param positive_event_name: name of the positive event which should be added if filter conditions is True
    :param filters: dict with filter conditions

    :type df: pd.DataFrame
    :type positive_event_name: str
    :type filters: dict
    :return: self
    :rtype: pd.DataFrame
    """
    logging.info('Start. Shape: {}'.format(df.shape))
    if filters is None:
        logging.info('Done. Shape: {}'.format(df.shape))
        return df
    head_match = filters.get('match_up_to_separator', {})
    full_match_list = filters.get('full_match', [])
    df.loc[:, 'target_event'] = 0
    if len(head_match):
        head_match_sep = head_match.get('sep', '_')
        head_match_list = head_match.get('values', [])
        if len(head_match_list):
            df.loc[df.event_name.str.split(head_match_sep, 1).str[0].isin(head_match_list), 'target_event'] = 1
    if len(full_match_list):
        df.loc[df.event_name.isin(full_match_list), 'target_event'] = 1
    if df.target_event.sum() != 0:
        # add the time of the first event "passed"
        first_positive_event = df.loc[df.target_event == 1, :] \
            .groupby('user_pseudo_id').event_timestamp.min() \
            .rename('event_timestamp_passed') \
            .reset_index()
        df = df.merge(first_positive_event, how='left', on=['user_pseudo_id'])

        # leave only events before the "passed" event
        df = df.loc[df.event_timestamp_passed.isnull() | (df.event_timestamp <= df.event_timestamp_passed), :]
        df.loc[df.target_event == 1, 'event_name'] = positive_event_name
        df = df.drop('event_timestamp_passed', axis=1)
    df = df.drop('target_event', axis=1)
    logging.info('Done. Shape: {}'.format(df.shape))
    return df

_minumum_time_delta = pd.Timedelta(seconds=1)
def add_lost_events(df, positive_event_name, negative_event_name):
    """
    Add new events with `negative_event_name` in input DataFrame.

    :param df: input pd.DataFrame
    :param positive_event_name: positive event name
    :param negative_event_name: negative event name which should be added if there is no positive event in the session

    :type df: pd.DataFrame
    :type positive_event_name: str
    :type negative_event_name: str
    :return: self
    :rtype: pd.DataFrame
    """
    logging.info('Start. Shape: {}'.format(df.shape))

    df = df.sort_values(['user_pseudo_id', 'event_timestamp'])
    last_row = df.groupby('user_pseudo_id', as_index=False).last()
    last_row = last_row.loc[
        last_row.event_name != positive_event_name, ['user_pseudo_id', 'event_name', 'event_timestamp']]
    if len(last_row):
        last_row.loc[:, 'event_name'] = negative_event_name
        last_row.loc[:, 'event_timestamp'] += _minumum_time_delta

        df = df.append(last_row, sort=False)
        df = df.sort_values(['user_pseudo_id', 'event_timestamp']).copy()
    logging.info('Done. Shape: {}'.format(df.shape))
    return df
