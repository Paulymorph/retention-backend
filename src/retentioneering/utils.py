import json
import yaml


class Config(dict):
    """
    Enrichment of dict class with saving option
    """

    def __init__(self, filename, is_json=False):
        """

        :param filename: str
            input file name
        :param is_json: bool
            read in json format (yaml otherwise)
        """
        with open(filename, 'rb') as f:
            super(Config, self).__init__(json.load(f)) if is_json else super(Config, self).__init__(yaml.load(f))

    def export(self, filename, is_json=False):
        """
        Dumps config to file

        :param filename: str
            output file name
        :param is_json: bool
            save in json format (yaml otherwise)
        :return:
        """
        with open(filename, 'wb') as f:
            json.dump(self, f) if is_json else yaml.dump(self, f)

