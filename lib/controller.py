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

"""Application controller."""

import atexit
import os
import signal
import sys
from time import sleep
from typing import Type

from . import log
from .config import Config
from .display import Display
from .event_manager import EventManager
from .events.button import ButtonEvents
from .events.timer import TimerEvents
from .events.tick import TickEvents
from .events.trigger import TriggerEvents
from .font_manager import FontManager
from .screen import Screen
from .screen_manager import ScreenManager
from .viewport import Viewport

POLL_INTERVAL = 0.1


class Controller:
    """The controller coordinates high level configuration, events, display, and lifecycle."""

    instances = 0

    def __init__(self, config_path: str):
        assert self.instances == 0
        base_folder = os.path.dirname(config_path)
        self.instances += 1
        self.config = Config(config_path)
        self.event_manager = EventManager()
        self.event_manager.add_producer('button', ButtonEvents())
        self.event_manager.add_producer('timer', TimerEvents())
        self.event_manager.add_producer('tick', TickEvents())
        self.event_manager.add_producer('trigger', TriggerEvents())
        # Event handlers must be flagged permanent in order to survive screen initialization.
        self.event_manager.register('timer', self.update, self.config.update_interval,
                                    permanent=True)
        self.event_manager.register('trigger', self.activate_screen, 'screen', permanent=True)
        # TODO: Don't hard-code these events.
        self.event_manager.register('button', self.on_button3, 3, permanent=True)
        self.event_manager.register('button', self.on_button4, 4, permanent=True)
        self.font_manager = FontManager(os.path.join(base_folder, 'fonts'))
        self.screen_manager = ScreenManager(self.event_manager)
        self.display = Display(self.config.display.left,
                               self.config.display.top,
                               self.config.display.width,
                               self.config.display.height,
                               self.config.display.device,
                               self.config.display.driver)
        self.display.clear()
        self.outer_viewport = Viewport(self.display, self.event_manager, self.display.rect)
        atexit.register(self.cleanup)

        def _signal_handler(signum, _frame):
            sys.exit(signum)

        signal.signal(signal.SIGTERM, _signal_handler)

    def add_screen(self, name, screen_class: Type[Screen]):
        """
        Add a named screen.

        :param name: screen name
        :param screen_class: screen class (not instance)
        """
        self.screen_manager.add_screen(name, screen_class(self.config,
                                                          self.event_manager,
                                                          self.font_manager))

    def update(self):
        """
        Called on a timer to check for configuration updates.
        """
        if self.config.update():
            log.info('Reloaded configuration.')
            self.screen_manager.force_refresh()

    def activate_screen(self, screen_name: str):
        """
        Activate a named screen.

        :param screen_name: screen name
        """
        self.screen_manager.show_screen(screen_name, self.outer_viewport)

    def on_button3(self):
        """
        Handle PiTFT button 3 by exiting application.

        TODO: Don't hard-code these events.
        """
        self.screen_manager.active_screen.message('Exiting...')
        sleep(2)
        sys.exit(0)

    def on_button4(self):
        """
        Handle PiTFT button 3 by shutting down the Raspberry Pi.

        TODO: Don't hard-code these events.
        """
        self.screen_manager.active_screen.message('Powering off...')
        sleep(2)
        os.execlp('sudo', 'sudo', 'poweroff')

    def cleanup(self):
        """
        Perform clean shutdown of device support, including the display.
        :return:
        """
        log.info('Cleaning up...')
        self.display.shut_down()

    def main(self, initial_screen_name):
        """
        Main application loop.

        Does not return unless an exception happens.

        :param initial_screen_name: initial active screen name
        """
        self.screen_manager.show_screen(initial_screen_name, self.outer_viewport)
        while True:
            self.event_manager.tick()
            sleep(POLL_INTERVAL)
