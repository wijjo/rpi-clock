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
from RPi import GPIO
from typing import Iterator, List

from rpiclock.utility import log

from .device import DeviceDriver
from .pygame_display import PygameDisplay

GPIO_PATH = '/usr/bin/gpio'
DEFAULT_BRIGHTNESS_FREQUENCY = 1000


class RPIDriver(DeviceDriver):
    """Hardware controller for Raspberry Pi."""

    def __init__(self,
                 width: int,
                 height: int,
                 framebuffer_device: str,
                 framebuffer_driver: str,
                 left: int = 0,
                 top: int = 0,
                 button_pins: List[int] = None,
                 brightness: int = None,
                 brightness_pin: int = None,
                 brightness_frequency: int = DEFAULT_BRIGHTNESS_FREQUENCY):
        """
        RPI driver constructor.

        Configuration params are converted to keyword style arguments that
        should meet this constructor's calling interface.

        :param width: screen width
        :param height: screen height
        :param framebuffer_device: framebuffer device path
        :param framebuffer_driver: framebuffer driver type name
        :param left: left origin (default=0)
        :param top: top origin (default=0)
        :param button_pins: button pin number list
        :param brightness: brightness, 0-255
        :param brightness_pin: brightness control pin number
        :param brightness_frequency: brightness control frequency (Hz)
        """
        log.debug('Initialize GPIO buttons.')
        self.left = left
        self.top = top
        self.width = width
        self.height = height
        self.framebuffer_device = framebuffer_device
        self.framebuffer_driver = framebuffer_driver
        self.button_pins = button_pins or []
        self.brightness = brightness
        self.brightness_pin = brightness_pin
        self.brightness_frequency = brightness_frequency
        self._initialize_gpio()
        self._initialize_brightness()

    def _initialize_gpio(self):
        if self.button_pins:
            GPIO.setmode(GPIO.BCM)
            for pin in self.button_pins:
                GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    def _initialize_brightness(self):
        if self.brightness and self.brightness_pin:
            if os.path.exists(GPIO_PATH):
                log.info(f'Set brightness to {self.brightness}.')
                commands = [f'{GPIO_PATH} -g mode {self.brightness_pin} pwm',
                            f'{GPIO_PATH} pwmc {self.brightness_frequency}',
                            f'{GPIO_PATH} -g pwm {self.brightness_pin} {self.brightness}']
                if os.system('; '.join(commands)) != 0:
                    log.error('Failed to change display brightness.')
            else:
                log.error('Unable to control brightness without "wiringpi" installed.')

    def get_display(self) -> PygameDisplay:
        """
        Provide object that implements display support.

        :return: Display sub-class instance
        """
        return PygameDisplay(self.left,
                             self.top,
                             self.width,
                             self.height,
                             self.framebuffer_device,
                             self.framebuffer_driver)

    def get_button_count(self) -> int:
        """
        Get the number of supported buttons.

        :return: button count
        """
        return len(self.button_pins)

    def iterate_pressed_buttons(self) -> Iterator[int]:
        """
        Iterate pressed button indexes.

        :return: button index [0-n] iterator for pressed buttons
        """
        for button_index, pin in enumerate(self.button_pins):
            if not GPIO.input(pin):
                yield button_index
