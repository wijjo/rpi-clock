import json


class Config:

    def __init__(self, path):
        with open(path) as open_file:
            self._data = json.load(open_file)

    def __getattr__(self, name):
        if name.startswith('_'):
            return getattr(self, name)
        return self._data.get(name)
