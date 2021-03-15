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

"""Time/date panel."""

from time import localtime, strftime
from typing import Optional

from .. import log
from ..display import COLOR_GHOST_TEXT
from ..event_manager import EventManager
from ..panel import Panel
from ..viewport import Viewport


class TimePanel(Panel):
    """Time/date panel."""

    def __init__(self, time_format: str, ghost_lcd: bool = False):
        """
        Time/date panel constructor.

        :param time_format: strftime()-compatible time/date format
        :param ghost_lcd: provided a ghosted LCD effect (works for LCD fonts only)
        """
        def _check_format(*letters: str) -> bool:
            for letter in letters:
                if f'%{letter}' in time_format:
                    return True
            return False
        super().__init__()
        self.time_format = time_format
        self.use_year = _check_format('y', 'Y')
        self.use_month = _check_format('b', 'B', 'm')
        self.use_day = _check_format('d', 'a', 'A')
        self.use_hour = _check_format('H', 'I')
        self.use_minute = _check_format('M')
        self.use_second = _check_format('S')
        self.local_time: Optional[float] = None
        self.ghost_text: Optional[str] = None
        if ghost_lcd:
            if self.time_format == '%H:%M':
                self.ghost_text = '88:88'
            elif self.time_format == '%S':
                self.ghost_text = '88'
            else:
                log.error(f'Unsupported time format {self.time_format}'
                          f' for LCD ghost effect.')

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
        if self.local_time is None:
            self.local_time = localtime()
        # The LCD ghost effect only works with specific formats.
        if self.ghost_text is not None:
            ghost_viewport = viewport.overlay(color=COLOR_GHOST_TEXT)
            ghost_viewport.text(self.ghost_text)
            viewport.text(strftime(self.time_format, self.local_time), overwrite=True)
        else:
            viewport.text(strftime(self.time_format, self.local_time))
        self.local_time = self.local_time

    def on_check(self) -> bool:
        """
        Required update check call-back.

        :return: True if panel needs to be refreshed.
        """
        t1 = self.local_time
        t2 = localtime()
        needs_refresh = (t1 is None
                         or (self.use_year and t1.tm_year != t2.tm_year)
                         or (self.use_month and t1.tm_mon != t2.tm_mon)
                         or (self.use_day and t1.tm_mday != t2.tm_mday)
                         or (self.use_hour and t1.tm_hour != t2.tm_hour)
                         or (self.use_minute and t1.tm_min != t2.tm_min)
                         or (self.use_second and t1.tm_sec != t2.tm_sec))
        self.local_time = t2
        return needs_refresh
