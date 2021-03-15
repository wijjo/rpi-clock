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

"""Event manager class."""

from time import time
from typing import Dict, Callable

from . import log
from .event_handler import EventHandler
from .event_producer import EventProducer


class EventManager:
    """Event manager."""

    def __init__(self):
        """Event manager constructor."""
        self.producers: Dict[str, EventProducer] = {}

    def clear(self):
        """
        Clear event producers.

        The producer decides what "clearing" means.
        """
        for event_producer in self.producers.values():
            event_producer.clear()

    def add_producer(self, producer_name: str, producer: EventProducer):
        """
        Add a named event producer.

        :param producer_name: producer name
        :param producer: producer implementation object
        """
        self.producers[producer_name] = producer

    def register(self, producer_name: str, function: Callable, *args, **kwargs):
        """
        Register an event handler.

        :param producer_name: event producer name
        :param function: handler function
        :param args: positional arguments passed to producer.register()
        :param kwargs: keyword arguments passed to producer.register()
        """
        handler = EventHandler(function, kwargs.pop('permanent', False))
        if producer_name in self.producers:
            self.producers[producer_name].register(handler, *args, **kwargs)
        else:
            log.error(f'Unable to register event for unknown producer "{producer_name}".')

    def send(self, producer_name: str, *args, **kwargs):
        """
        Send data to an event producer.

        Not all producers will support or do anything with this.

        :param producer_name: producer name
        :param args: positional arguments to send
        :param kwargs: keyword arguments to send
        """
        if producer_name in self.producers:
            self.producers[producer_name].send(*args, **kwargs)
        else:
            log.error(f'Unable to send data to unknown producer "{producer_name}".')

    def tick(self):
        """
        Tick handles periodic (frequent) global timed updates.

        Each producer handles the tick event differently.
        """
        for event_producer in self.producers.values():
            t1 = time()
            event_producer.tick()
            t2 = time()
            if t2 - t1 > .1:
                log.warning(f'Slow {event_producer.display_name()} event'
                            f' producer took {t2 - t1:.2f} seconds.')
