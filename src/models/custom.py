from flask.json import JSONEncoder

from src.models.event import Event


class CustomJSONEncoder(JSONEncoder):

    def default(self, obj):
        try:
            if isinstance(obj, Event):
                return obj.serialize()

            raise RuntimeError("Not defined serialization for %s %s" % (type(obj), obj))
        except TypeError as ex:
            print("Error occurred while serializing %s. %s" % (obj, ex))

        return JSONEncoder.default(self, obj)
