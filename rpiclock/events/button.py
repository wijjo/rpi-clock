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

"""GPIO button event producer."""

from RPi import GPIO
from typing import List, Optional

from rpiclock import log
from rpiclock.controller.event_handler import EventHandler
from rpiclock.controller.event_producer import EventProducer


class ButtonEvents(EventProducer):
    """GPIO button event producer."""

    def __init__(self, button_pins: List[int]):
        """Constructor."""
        self.button_pins = button_pins
        self.button_handlers: List[Optional[EventHandler]] = [None] * len(self.button_pins)
        log.debug('Initialize GPIO.')
        GPIO.setmode(GPIO.BCM)
        for pin in self.button_pins:
            GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    # noinspection PyMethodOverriding
    def register(self, handler: EventHandler, button_idx: int):
        """
        Register button event handler.

        :param handler: event handler
        :param button_idx: button index, 1 to button count
        """
        if 0 < button_idx <= len(self.button_pins):
            self.button_handlers[button_idx - 1] = handler
        else:
            log.error(f'Unable to register event for bad button index: {button_idx}')

    def tick(self):
        """Polling call-back to check buttons and invoke handlers."""
        for pin_idx, pin in enumerate(self.button_pins):
            if not GPIO.input(pin):
                if self.button_handlers[pin_idx] is not None:
                    self.button_handlers[pin_idx].function()

    def clear(self):
        """Clear all button handlers."""
        for pin_idx, pin in enumerate(self.button_pins):
            if (self.button_handlers[pin_idx] is not None
                    and not self.button_handlers[pin_idx].permanent):
                self.button_handlers[pin_idx] = None

    def send(self, *args, **kwargs):
        """Unsupported required call-back for generating explicit event."""
        log.error('Button event producer does not support send().')

    def display_name(self) -> str:
        """
        Friendly/useful display text.

        :return: display text
        """
        return f'Button[{len(self.button_handlers)} handlers]'
