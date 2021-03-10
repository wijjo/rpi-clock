import json
import os
from dataclasses import dataclass
from typing import Any, Optional


class ConfigDict(dict):

    def __init__(self, data: dict):
        super().__init__(data)

    def __getattr__(self, name: str) -> Optional[Any]:
        return self._wrap_data(self.get(name))

    def __getitem__(self, name: str) -> Optional[Any]:
        return self._wrap_data(self.get(name))

    @classmethod
    def _wrap_data(cls, data: Any) -> Any:
        if isinstance(data, dict):
            return cls(data)
        if isinstance(data, list):
            return [cls._wrap_data(item) for item in data]
        return data


class Config:
    """
    Load and access configuration JSON through attributes or indexes.

    It only supports a config file with a dictionary outer structure.
    """

    @dataclass
    class Meta:
        path: str
        timestamp: float

    def __init__(self, path):
        self._meta = self.Meta(path, 0)
        self._data = ConfigDict({})
        self.update()

    def update(self) -> bool:
        timestamp = os.path.getmtime(self._meta.path)
        if timestamp != self._meta.timestamp:
            with open(self._meta.path, encoding='utf-8') as open_file:
                self._data = ConfigDict(json.load(open_file))
                self._meta.timestamp = timestamp
                return True
        return False

    def __getattr__(self, name: str) -> Optional[Any]:
        if name.startswith('_'):
            return getattr(self, name)
        return self._data[name]

    def __getitem__(self, name: str) -> Optional[Any]:
        return self._data[name]
