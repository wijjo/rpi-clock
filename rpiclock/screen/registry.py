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

"""Screen switcher/manager."""

from typing import Optional, Dict

from rpiclock.events import EventProducersRegistry
from rpiclock.utility import log

from .panel import Panel
from .viewport import Viewport
from .screen import Screen


class ScreenPanel:
    """Viewport/panel assignment."""
    def __init__(self, viewport: Viewport, panel: Panel):
        self.viewport = viewport
        self.panel = panel


class ScreensRegistry:
    """Screen switcher/manager."""

    def __init__(self, event_producers_registry: EventProducersRegistry):
        """
        Screen manager constructor.

        :param event_producers_registry: event manager for registering and clearing events
        """
        self.event_producers_registry = event_producers_registry
        self.screens: Dict[str, Screen] = {}
        self.current: Optional[str] = None

    def add_screen(self, name: str, screen: Screen):
        """
        Register a named screen.

        :param name: screen name
        :param screen: screen object
        """
        self.screens[name] = screen

    def show_screen(self, name: str, outer_viewport: Viewport):
        """
        Show/activate a named screen.

        :param name: screen name
        :param outer_viewport: outer viewport used for display
        """
        if name != self.current:
            self.event_producers_registry.clear()
            if name in self.screens:
                self.screens[name].initialize(outer_viewport)
                self.current = name
            else:
                log.error(f'Unable to show unknown screen name "{name}".')
                self.current = None

    @property
    def active_screen(self) -> Optional[Screen]:
        """
        Property for current active screen.

        :return: active screen or None if nothing is active.
        """
        return self.screens.get(self.current)

    def force_refresh(self):
        """Force a full screen refresh."""
        if self.current is not None:
            log.info('Force screen refresh.')
            self.screens[self.current].refresh()
