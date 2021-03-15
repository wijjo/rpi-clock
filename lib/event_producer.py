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

"""Event producer base class."""

from .event_handler import EventHandler


class EventProducer:
    """Event producer base class."""

    def register(self, handler: EventHandler, *args, **kwargs):
        """
        Required override to register a handler.

        :param handler: handler, including the handler function and permanent flag
        :param args: positional parameters for the producer
        :param kwargs: keyword parameters for the producer
        """
        raise NotImplementedError

    def clear(self):
        """Clear handlers."""
        raise NotImplementedError

    def tick(self):
        """Handler global tick event."""
        raise NotImplementedError

    def send(self, *args, **kwargs):
        """
        Send a programmatic event.

        :param args: positional parameters for the producer
        :param kwargs: keyword parameters for the producer
        """
        raise NotImplementedError

    def display_name(self) -> str:
        """
        Informative display name provided by producer, that may include some state.

        :return: display name
        """
        raise NotImplementedError
