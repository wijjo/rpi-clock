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

from rpiclock.events import EventProducersRegistry
from rpiclock.screen import Viewport, Panel
from rpiclock.utility.typing import Interval

from .registry import PanelRegistry


@PanelRegistry.register('message')
class MessagePanel(Panel):
    """Message panel."""

    def __init__(self):
        """Constructor."""
        self.text: Optional[str] = None
        self.previous_text: Optional[str] = None
        self.duration: Optional[Interval] = None

    def set_message(self, text: str, duration: Interval = None):
        """
        Set message text with optional timed clearing.

        :param text: message text
        :param duration: optional duration interval for automatic clearing
        """
        self.text = text
        self.duration = duration

    def on_initialize(self,
                      event_producers_registry: EventProducersRegistry,
                      viewport: Viewport):
        """
        Required event initialization call-back.

        :param event_producers_registry: event producers registry
        :param viewport: display viewport
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
