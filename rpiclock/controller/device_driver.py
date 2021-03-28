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

"""Base hardware driver."""

from typing import Iterator, Optional, Dict, List

from rpiclock.view.display import Display


class _Required:
    pass


PARAM_REQUIRED = _Required


class DeviceDriver:
    """Base class for hardware driver."""

    def __init__(self, params: Optional[Dict], **meta):
        """
        Device driver constructor.

        :param params: driver configuration parameters
        :param meta: param metadata
        """
        self.params = params or {}
        if meta:
            missing: List[str] = []
            for name, value in meta.items():
                if name not in self.params:
                    if value is _Required:
                        missing.append(name)
                    else:
                        self.params[name] = value
            if missing:
                raise ValueError(f'Missing {self.__class__.__name__} params: {" ".join(missing)}')

    def get_display(self) -> Display:
        """
        Provide object that implements display support.

        :return: Display sub-class instance
        """
        raise NotImplementedError

    def get_button_count(self) -> int:
        """
        Get the number of supported buttons.

        :return: button count
        """
        raise NotImplementedError

    def iterate_pressed_buttons(self) -> Iterator[int]:
        """
        Iterate pressed button indexes.

        :return: button index [0-n] iterator for pressed buttons
        """
        raise NotImplementedError

    def set_brightness(self, brightness: int):
        """
        Set display brightness.

        :param brightness: brightness value (understood by sub-class)
        """
        raise NotImplementedError
