import json
import os
from dataclasses import dataclass


class Config:

    @dataclass
    class Meta:
        path: str
        timestamp: float

    def __init__(self, path):
        self._meta = self.Meta(path, 0)
        self._data = {}
        self.update()

    def update(self) -> bool:
        timestamp = os.path.getmtime(self._meta.path)
        if timestamp != self._meta.timestamp:
            with open(self._meta.path, encoding='utf-8') as open_file:
                self._data = json.load(open_file)
                self._meta.timestamp = timestamp
                return True
        return False

    def __getattr__(self, name):
        if name.startswith('_'):
            return getattr(self, name)
        return self._data.get(name)
