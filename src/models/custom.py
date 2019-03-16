import datetime
import logging

from coremltools.models.model import MLModel
from flask.json import JSONEncoder

from src.models.event import Event


class CustomJSONEncoder(JSONEncoder):

    def default(self, obj):
        try:
            if isinstance(obj, Event):
                return obj.serialize()

            if isinstance(obj, MLModel):
                from google.protobuf.json_format import MessageToDict
                dict_obj = MessageToDict(obj.get_spec())
                return dict_obj

            if isinstance(obj, datetime.datetime):
                return str(obj.strftime('%Y-%m-%d %H:%M:%S.%f'))

            raise RuntimeError("Not defined serialization for %s %s" % (type(obj), obj))
        except TypeError as ex:
            logging.warn("Error occurred while serializing %s. %s" % (obj, ex))

        return JSONEncoder.default(self, obj)
