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

from rpiclock.drivers import DeviceDriver, RPIDriver
from rpiclock.events import ButtonEvents, TickEvents, TimerEvents, TriggerEvents, EventProducersRegistry
from rpiclock.screen import ScreensRegistry, Screen, Viewport
from rpiclock.utility import Config, log, FontsFinder

DEFAULT_POLL_INTERVAL = 0.1


class MainController:
    """The controller coordinates high level configuration, events, display, and lifecycle."""

    instances = 0

    def __init__(self, config_path: str):
        assert self.instances == 0
        log.info(f'Create controller (PID={os.getpid()}).')
        base_folder = os.path.dirname(config_path)
        self.instances += 1
        self.config = Config(config_path)
        self.poll_interval = self.config.poll_interval or DEFAULT_POLL_INTERVAL
        self.driver = self._initialize_driver()
        self.event_producers_registry = self._initialize_events()
        self.fonts_finder = FontsFinder(os.path.join(base_folder, 'fonts'))
        self.screens_registry = ScreensRegistry(self.event_producers_registry)
        self.display = self.driver.get_display()
        self.outer_viewport = Viewport(self.display,
                                       self.event_producers_registry,
                                       self.display.rect)
        self.outer_viewport.clear()
        atexit.register(self.cleanup)

        def _signal_handler(signum, _frame):
            sys.exit(signum)

        signal.signal(signal.SIGTERM, _signal_handler)
        signal.signal(signal.SIGINT, _signal_handler)

    def _initialize_driver(self) -> DeviceDriver:
        # noinspection PyBroadException
        try:
            if not self.config.device["class"]:
                raise ValueError(f'No device.class specified in configuration.')
            # "rpi" is the only supported driver class for now.
            if self.config.device["class"] != 'rpi':
                raise ValueError(f'Bad device.class "{self.config.device["class"]}".')
            return RPIDriver(**(self.config.device.params or {}))
        except Exception as exc:
            log.critical(exc)
            sys.exit(1)

    def _initialize_events(self) -> EventProducersRegistry:
        event_producers_registry = EventProducersRegistry()
        button_event_producer = ButtonEvents(self.driver)
        event_producers_registry.add_producer('button', button_event_producer)
        event_producers_registry.add_producer('timer', TimerEvents())
        event_producers_registry.add_producer('tick', TickEvents())
        event_producers_registry.add_producer('trigger', TriggerEvents())
        # Event handlers must be flagged permanent in order to survive screen initialization.
        event_producers_registry.register('timer',
                                          self.update,
                                          self.config.update_interval,
                                          permanent=True)
        event_producers_registry.register('trigger',
                                          self.activate_screen,
                                          'screen',
                                          permanent=True)
        # Supported buttons actions are "quit", "poweroff", "screen1", and "screen2".
        if self.config.buttons.quit:
            event_producers_registry.register('button',
                                              self.on_quit,
                                              self.config.buttons.quit,
                                              permanent=True)
        if self.config.buttons.poweroff:
            event_producers_registry.register('button',
                                              self.on_poweroff,
                                              self.config.buttons.poweroff,
                                              permanent=True)
        if self.config.buttons.screen1:
            event_producers_registry.register('button',
                                              self.on_screen1,
                                              self.config.buttons.screen1,
                                              permanent=True)
        if self.config.buttons.screen2:
            event_producers_registry.register('button',
                                              self.on_screen2,
                                              self.config.buttons.screen2,
                                              permanent=True)
        return event_producers_registry

    def add_screen(self, name, screen_class: Type[Screen]) -> Screen:
        """
        Add named screen.

        :param name: screen name
        :param screen_class: screen class (not instance)
        :return: screen instance
        """
        log.info(f'Add screen "{name}".')
        screen = screen_class(name, self.config, self.event_producers_registry, self.fonts_finder)
        self.screens_registry.add_screen(name, screen)
        return screen

    def update(self):
        """
        Called periodically to check for configuration updates.
        """
        if self.config.update():
            log.info('Reloaded configuration.')
            self.screens_registry.force_refresh()

    def activate_screen(self, name: str):
        """
        Activate named screen.

        :param name: screen name
        """
        log.info(f'Activate screen "{name}".')
        self.screens_registry.show_screen(name, self.outer_viewport)

    def on_quit(self):
        """Handle button by quitting application."""
        self.screens_registry.active_screen.message('Exiting...')
        sleep(2)
        sys.exit(0)

    def on_poweroff(self):
        """Handle button by powering off the Raspberry Pi."""
        self.screens_registry.active_screen.message('Powering off...')
        sleep(2)
        os.execlp('sudo', 'sudo', 'poweroff')

    def on_screen1(self):
        """Handle button by switching to screen #1."""
        self.event_producers_registry.send('trigger', 'screen', 'main')

    def on_screen2(self):
        """Handle button by switching to screen #1."""
        self.event_producers_registry.send('trigger', 'screen', 'screen2')

    def cleanup(self):
        """
        Perform clean shutdown of device support, including the display.
        :return:
        """
        self.display.shut_down()

    def main(self, initial_screen_name):
        """
        Main application loop.

        Does not return unless an exception happens.

        :param initial_screen_name: initial active screen name
        """
        # Handle Control-C exception cleanly.
        try:
            self.screens_registry.show_screen(initial_screen_name, self.outer_viewport)
            log.info('Start main loop.')
            while True:
                self.event_producers_registry.tick()
                sleep(self.poll_interval)
        except KeyboardInterrupt:
            sys.stderr.write(os.linesep)
            sys.exit(2)
