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

"""Explicitly-triggered event producer."""

from typing import Dict, List, Callable

from rpiclock.utility import log

from .handler import EventHandler
from .producer import EventProducer


class TriggerEvent:
    def __init__(self, function: Callable, args: list, kwargs: dict):
        self.function = function
        self.args = args
        self.kwargs = kwargs


class TriggerEvents(EventProducer):
    """The trigger event producer supports manually-generated named events."""

    def __init__(self):
        """Constructor."""
        self.permanent_handlers: Dict[str, Callable] = {}
        self.temporary_handlers: Dict[str, Callable] = {}
        self.triggers: List[TriggerEvent] = []

    # noinspection PyMethodOverriding
    def register(self, handler: EventHandler, trigger_name: str):
        """
        Register event handler.

        :param handler: handler to register
        :param trigger_name: trigger name for event
        """
        if handler.permanent:
            self.permanent_handlers[trigger_name] = handler.function
        else:
            self.temporary_handlers[trigger_name] = handler.function

    def tick(self):
        """Polled to generate events."""
        for trigger in self.triggers:
            trigger.function(*trigger.args, **trigger.kwargs)
        self.triggers = []

    def clear(self):
        """Clear temporary handlers and triggers."""
        self.temporary_handlers = {}
        self.triggers = []

    def send(self, *args, **kwargs):
        """
        Send explicit trigger event.

        If there is no trigger handler assumes the first positional argument is
        a handler function.

        :param args: positional arguments passed to handler
        :param kwargs: keyword arguments passed to handler
        """
        trigger_name = args[0]
        function = self.permanent_handlers.get(trigger_name)
        if not function:
            function = self.temporary_handlers.get(trigger_name)
        if function is not None:
            self.triggers.append(TriggerEvent(function, list(args[1:]), kwargs))
        else:
            log.error(f'Unknown trigger name "{trigger_name}" sent.')

    def display_name(self) -> str:
        """
        Friendly display text.

        :return: display text
        """
        handler_count = len(self.permanent_handlers) + len(self.temporary_handlers)
        trigger_count = len(self.triggers)
        return f'Timer[{handler_count} handlers, {trigger_count} triggers]'
