# Copyright (C) 2021, Steven Cooper
#
# This file is part of rpi-clock.
#
# Rpi-clock is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Rpi-clock is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with rpi-clock.  If not, see <https://www.gnu.org/licenses/>.

"""JSON configuration file support."""

import json
import os
from dataclasses import dataclass
from typing import Any, Optional


class ConfigDict(dict):
    """Configuration dictionary providing dual index-based and attribute access."""

    def __init__(self, data: dict):
        """
        Configuration dictionary constructor.

        :param data: initial data dictionary
        """
        super().__init__(data)

    def __getattr__(self, name: str) -> Optional[Any]:
        """
        Attribute-based read access.

        :param name: attribute name
        :return: value if name is found, None otherwise
        """
        return self._wrap_data(self.get(name))

    def __getitem__(self, name: str) -> Optional[Any]:
        """
        Dictionary index-based read access.

        :param name: attribute name
        :return: value if name is found, None otherwise
        """
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
    class FileMetadata:
        """Configuration file meta-data."""
        path: str
        timestamp: float

    def __init__(self, path):
        """
        Configuration constructor.

        :param path: configuration file path
        """
        self._meta = self.FileMetadata(path, 0)
        self._data = ConfigDict({})
        self.update()

    def update(self) -> bool:
        """
        Update configuration if the file has changed.

        :return: True if the configuration was updated
        """
        timestamp = os.path.getmtime(self._meta.path)
        if timestamp != self._meta.timestamp:
            with open(self._meta.path, encoding='utf-8') as open_file:
                self._data = ConfigDict(json.load(open_file))
                self._meta.timestamp = timestamp
                return True
        return False

    def __getattr__(self, name: str) -> Optional[Any]:
        """
        Attribute-based read access to top level items.

        Data is returned fully wrapped so that attributes or indexes may be used
        for access to child elements.

        :param name: attribute name
        :return: value if name is found, None otherwise
        """
        if name.startswith('_'):
            return getattr(self, name)
        return self._data[name]

    def __getitem__(self, name: str) -> Optional[Any]:
        """
        Dictionary index-based read access to top level items.

        Data is returned fully wrapped so that attributes or indexes may be used
        for access to child elements.

        :param name: attribute name
        :return: value if name is found, None otherwise
        """
        return self._data[name]
