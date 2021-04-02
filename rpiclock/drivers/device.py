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

from typing import Iterator

from .display import Display


class _Required:
    pass


class DeviceDriver:
    """Base class for hardware driver."""

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
