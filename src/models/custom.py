from flask.json import JSONEncoder

from src.models.event import Event
from coremltools.models.model import MLModel


class CustomJSONEncoder(JSONEncoder):

    def default(self, obj):
        try:
            if isinstance(obj, Event):
                return obj.serialize()

            if isinstance(obj, MLModel):
                from google.protobuf.json_format import MessageToDict
                dict_obj = MessageToDict(obj.get_spec())
                return dict_obj

            raise RuntimeError("Not defined serialization for %s %s" % (type(obj), obj))
        except TypeError as ex:
            print("Error occurred while serializing %s. %s" % (obj, ex))

        return JSONEncoder.default(self, obj)
