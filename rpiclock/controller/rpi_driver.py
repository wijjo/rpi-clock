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

"""Raspberry Pi hardware driver."""

import os
from contextlib import contextmanager
from RPi import GPIO
from typing import Sequence, Iterator, Optional

from rpiclock import log
from rpiclock.controller.base_driver import BaseDriver


class RPIDriver(BaseDriver):
    """Hardware controller for Raspberry Pi."""

    gpio_path = '/usr/bin/gpio'
    default_brightness_frequency = 1000

    def __init__(self,
                 button_pins: Optional[Sequence[int]],
                 brightness_pin: Optional[int],
                 brightness_frequency: Optional[int],
                 brightness: Optional[int]):
        """
        RPI driver constructor.

        :param button_pins: support button pin GPIO numbers
        :param brightness_pin: PWM control pin GPIO number
        :param brightness_frequency: PWM control frequency
        :param brightness: initial brightness value
        """
        self.button_pins = button_pins
        self.brightness_pin = brightness_pin
        self.brightness_frequency = brightness_frequency or self.default_brightness_frequency
        log.debug('Initialize GPIO buttons.')
        if self.button_pins:
            with self.gpio_mode(GPIO.BCM):
                for pin in button_pins:
                    GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        if brightness is not None and self.brightness_pin:
            self.set_brightness(brightness)

    @classmethod
    @contextmanager
    def gpio_mode(cls, mode: int):
        """
        Set and restore mode when exiting context.

        :param mode: GPIO mode to set
        """
        previous_mode = GPIO.getmode()
        if mode != previous_mode:
            GPIO.setmode(mode)
        yield
        if previous_mode is not None and mode != previous_mode:
            GPIO.setmode(previous_mode)

    def get_button_count(self) -> int:
        """
        Get the number of supported buttons.

        :return: button count
        """
        return len(self.button_pins) if self.button_pins else 0

    def iterate_pressed_buttons(self) -> Iterator[int]:
        """
        Iterate pressed button indexes.

        :return: button index [0-n] iterator for pressed buttons
        """
        if self.button_pins:
            for button_index, pin in enumerate(self.button_pins):
                if not GPIO.input(pin):
                    yield button_index

    def set_brightness(self, brightness: int):
        """
        Set display brightness.

        Uses the wiringpi gpio program, because RPi.GPIO does not support the
        hardware clock from Python.

        :param brightness: brightness value (understood by sub-class)
        """
        if self.brightness_pin:
            if os.path.exists(self.gpio_path):
                log.info(f'Set brightness to {brightness}.')
                commands = [f'{self.gpio_path} -g mode {self.brightness_pin} pwm',
                            f'{self.gpio_path} pwmc {self.brightness_frequency}',
                            f'{self.gpio_path} -g pwm {self.brightness_pin} {brightness}']
                if os.system('; '.join(commands)) != 0:
                    log.error('Failed to change display brightness.')
            else:
                log.error('Unable to control brightness without "wiringpi" installed.')
