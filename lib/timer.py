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

"""General-purpose timer."""

from time import time
from typing import Callable

from .typing import Interval


class Timer:
    """
    General-purpose timer class.

    Must be frequently polled, e.g. 10 times/second by calling check().
    """

    def __init__(self,
                 interval: Interval,
                 function: Callable[[], None],
                 max_count: int = None,
                 ):
        """
        Timer constructor.

        :param interval: timing interval in seconds.
        :param function:
        :param max_count:
        """
        self.interval = interval
        self.function = function
        # max_count can be a countdown quantity or None for infinite.
        self.max_count = max_count
        self._count = 0
        # timed event is inactive when _next_time is None.
        self._next_time = time() + self.interval

    def check(self, check_time: float = None):
        """
        Polled call-back to check for interval expiration.

        :param check_time: explicit time to check against, defaults to current time
        """
        if self._next_time is None:
            return False
        time_to_check = check_time or time()
        if time_to_check < self._next_time:
            return False
        self._count += 1
        if self.max_count is None or self._count < self.max_count:
            self._next_time = time_to_check + self.interval
        else:
            self._next_time = None
        self.function()
        return True

    def is_active(self) -> bool:
        """
        Check if timer is active.

        :return: True if active
        """
        return self._next_time is not None
