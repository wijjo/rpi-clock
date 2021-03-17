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

from rpiclock.controller.event_manager import EventManager
from rpiclock.view.viewport import Viewport


class Panel:
    """Display panel base class."""

    def on_initialize_events(self, event_manager: EventManager):
        """
        Required override to handle event initialization.

        The Panel sub-class should register handlers here.

        :param event_manager: event manager to handle registration
        """
        raise NotImplementedError

    def on_display(self, viewport: Viewport):
        """
        Required override to handle display.

        :param viewport: outer viewport
        """
        raise NotImplementedError

    def on_check(self) -> bool:
        """
        Required override to check for changes.

        :return: True if data has been updated that needs to be displayed
        """
        raise NotImplementedError
