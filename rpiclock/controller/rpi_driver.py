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
from typing import Iterator, Optional, Dict

from rpiclock import log
from rpiclock.view.pygame_display import PygameDisplay

from .device_driver import DeviceDriver, PARAM_REQUIRED

GPIO_PATH = '/usr/bin/gpio'
DEFAULT_BRIGHTNESS_FREQUENCY = 1000


class RPIDriver(DeviceDriver):
    """Hardware controller for Raspberry Pi."""

    def __init__(self, params: Optional[Dict]):
        """
        RPI driver constructor.

        :param params: driver configuration parameters
        """
        super().__init__(params,
                         left=0,
                         top=0,
                         width=PARAM_REQUIRED,
                         height=PARAM_REQUIRED,
                         framebuffer_device=PARAM_REQUIRED,
                         framebuffer_driver=PARAM_REQUIRED,
                         button_pins=[],
                         brightness=None,
                         brightness_pin=None,
                         brightness_frequence=DEFAULT_BRIGHTNESS_FREQUENCY)

        log.debug('Initialize GPIO buttons.')
        if self.params['button_pins']:
            GPIO.setmode(GPIO.BCM)
            for pin in self.params['button_pins']:
                GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        if self.params['brightness'] and self.params['brightness_pin']:
            self.set_brightness(self.params['brightness'])

    def get_display(self) -> PygameDisplay:
        """
        Provide object that implements display support.

        :return: Display sub-class instance
        """
        return PygameDisplay(self.params['left'],
                             self.params['top'],
                             self.params['width'],
                             self.params['height'],
                             self.params['framebuffer_device'],
                             self.params['framebuffer_driver'])

    def get_button_count(self) -> int:
        """
        Get the number of supported buttons.

        :return: button count
        """
        return len(self.params['button_pins'])

    def iterate_pressed_buttons(self) -> Iterator[int]:
        """
        Iterate pressed button indexes.

        :return: button index [0-n] iterator for pressed buttons
        """
        for button_index, pin in enumerate(self.params['button_pins']):
            if not GPIO.input(pin):
                yield button_index

    def set_brightness(self, brightness: int):
        """
        Set display brightness.

        Uses the wiringpi gpio program, because RPi.GPIO does not support the
        hardware clock from Python.

        :param brightness: brightness value (understood by sub-class)
        """
        if self.params['brightness_pin']:
            if os.path.exists(GPIO_PATH):
                log.info(f'Set brightness to {brightness}.')
                commands = [f'{GPIO_PATH} -g mode {self.params["brightness_pin"]} pwm',
                            f'{GPIO_PATH} pwmc {self.params["brightness_frequency"]}',
                            f'{GPIO_PATH} -g pwm {self.params["brightness_pin"]} {brightness}']
                if os.system('; '.join(commands)) != 0:
                    log.error('Failed to change display brightness.')
            else:
                log.error('Unable to control brightness without "wiringpi" installed.')
