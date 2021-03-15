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

"""Timer event support."""

from time import time
from typing import List

from .. import log
from ..event_handler import EventHandler
from ..event_producer import EventProducer
from ..timer import Timer
from ..typing import Interval


class TimerEvents(EventProducer):
    """Timer event producer."""

    def __init__(self):
        """Timer event producer constructor."""
        self.permanent_timers: List[Timer] = []
        self.temporary_timers: List[Timer] = []

    # noinspection PyMethodOverriding
    def register(self,
                 handler: EventHandler,
                 interval: Interval,
                 max_count: int = None,
                 ):
        """
        Register timer event handler.

        Note that this register() method overload hard-codes the only supported
        arguments for clarity.

        :param handler: timer event handler
        :param interval: timer interval
        :param max_count: maximum repetitions or None for infinite
        """
        timer = Timer(interval, handler.function, max_count=max_count)
        if handler.permanent:
            self.permanent_timers.append(timer)
        else:
            self.temporary_timers.append(timer)

    def tick(self):
        """Polled call-back for timer checking and handler calling."""
        time_now = time()
        # Check permanent timers.
        active_permanent_timers = []
        for timer in self.permanent_timers:
            # Check if the handler should be called (by timer.check()).
            if timer.is_active():
                timer.check(check_time=time_now)
            # Keep track if it's still active.
            if timer.is_active():
                active_permanent_timers.append(timer)
        self.permanent_timers = active_permanent_timers
        # Check temporary timers.
        active_temporary_timers = []
        for timer in self.temporary_timers:
            # Check if the handler should be called (by timer.check()).
            if timer.is_active():
                timer.check(check_time=time_now)
            # Keep track if it's still active.
            if timer.is_active():
                active_temporary_timers.append(timer)
        self.temporary_timers = active_temporary_timers

    def clear(self):
        """Clear temporary timers."""
        self.temporary_timers = []

    def send(self, *args, **kwargs):
        """Unsupported, but required method to send an explicit event."""
        log.error('Timer event producer does not support send().')

    def display_name(self) -> str:
        """
        Required override to provide useful display text for logging.

        :return: display text
        """
        handler_count = len(self.permanent_timers) + len(self.temporary_timers)
        return f'Timer[{handler_count} handlers]'
