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

"""Button event producer."""

from typing import List, Optional

from rpiclock import log
from rpiclock.controller.base_driver import BaseDriver
from rpiclock.controller.event_handler import EventHandler
from rpiclock.controller.event_producer import EventProducer


class ButtonEvents(EventProducer):
    """Button event producer."""

    def __init__(self, driver: BaseDriver):
        """Constructor."""
        self.driver = driver
        self.button_count = driver.get_button_count()
        self.button_handlers: List[Optional[EventHandler]] = [None] * self.button_count

    # noinspection PyMethodOverriding
    def register(self, handler: EventHandler, button_number: int):
        """
        Register button event handler.

        :param handler: event handler
        :param button_number: button number, 1 through button count
        """
        if 0 < button_number <= self.button_count:
            self.button_handlers[button_number - 1] = handler
        else:
            log.error(f'Unable to register event for bad button index: {button_number}')

    def tick(self):
        """Polling call-back to check buttons and invoke handlers."""
        for button_number in self.driver.iterate_pressed_buttons():
            if self.button_handlers[button_number] is not None:
                self.button_handlers[button_number].function()

    def clear(self):
        """Clear all button handlers."""
        for button_idx in range(self.button_count):
            if (self.button_handlers[button_idx] is not None
                    and not self.button_handlers[button_idx].permanent):
                self.button_handlers[button_idx] = None

    def send(self, *args, **kwargs):
        """Unsupported required call-back for generating explicit event."""
        log.error('Button event producer does not support send().')

    def display_name(self) -> str:
        """
        Friendly/useful display text.

        :return: display text
        """
        return f'Button[{len(self.button_handlers)} handlers]'
