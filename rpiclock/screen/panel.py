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

"""Display panel base class."""

from rpiclock.events import EventProducersRegistry

from .viewport import Viewport


class Panel:
    """Display panel base class."""

    def on_initialize(self, event_producers_registry: EventProducersRegistry, viewport: Viewport):
        """
        Required override to handle event initialization.

        The Panel sub-class should register handlers here.

        The viewport allows the panel to initialize anything that might depend
        on viewport dimensions, etc..

        :param event_producers_registry: event manager to handle registration
        :param viewport: viewport for panel display
        """
        raise NotImplementedError

    def on_display(self, viewport: Viewport):
        """
        Required override to handle display.

        :param viewport: viewport for panel display
        """
        raise NotImplementedError

    def on_check(self) -> bool:
        """
        Required override to check for changes.

        :return: True if data has been updated that needs to be displayed
        """
        raise NotImplementedError
