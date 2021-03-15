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

"""Polled "tick" event producer."""

from typing import List, Callable

from .. import log
from ..event_handler import EventHandler
from ..event_producer import EventProducer


class TickEvents(EventProducer):
    """Polled "tick" event producer."""

    def __init__(self):
        """Constructor."""
        self.permanent_tick_handlers: List[Callable] = []
        self.temporary_tick_handlers: List[Callable] = []

    # noinspection PyMethodOverriding
    def register(self, handler: EventHandler):
        """
        Register event handler.

        :param handler: handler to register
        """
        if handler.permanent:
            self.permanent_tick_handlers.append(handler.function)
        else:
            self.temporary_tick_handlers.append(handler.function)

    def tick(self):
        """Polled to generate events."""
        for tick_function in self.temporary_tick_handlers + self.permanent_tick_handlers:
            tick_function()

    def clear(self):
        """Clear temporary handlers."""
        self.temporary_tick_handlers = []

    def send(self, *args, **kwargs):
        """Send explicit event (unsupported)."""
        log.error('Tick event producer does not support send().')

    def display_name(self) -> str:
        """
        Friendly display text.

        :return: display text
        """
        handler_count = len(self.temporary_tick_handlers) + len(self.permanent_tick_handlers)
        return f'Tick[{handler_count} handlers]'
