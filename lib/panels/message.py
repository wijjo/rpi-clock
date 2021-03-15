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

"""Message panel."""

from typing import Optional

from ..event_manager import EventManager
from ..panel import Panel
from ..typing import Interval
from ..viewport import Viewport


class MessagePanel(Panel):
    """Message panel."""

    def __init__(self):
        """Constructor."""
        self.text: Optional[str] = None
        self.previous_text: Optional[str] = None
        self.duration: Optional[Interval] = None

    def set(self, text: str, duration: Interval = None):
        """
        Set message text.

        :param text: message text
        :param duration: optional duration interval for automatic clearing
        """
        self.text = text
        self.duration = duration

    def on_initialize_events(self, event_manager: EventManager):
        """
        Required event initialization call-back.

        :param event_manager: event manager
        """
        # No events handled here.
        pass

    def on_display(self, viewport: Viewport):
        """
        Required display call-back.

        :param viewport: viewport for displaying panel.
        """
        if self.text is not None:
            viewport.text(self.text, duration=self.duration)
            self.previous_text = self.text

    def on_check(self) -> bool:
        """
        Required update check call-back.

        :return: True if panel needs to be refreshed.
        """
        return (self.text is not None
                and (self.previous_text is None
                     or self.text != self.previous_text))
