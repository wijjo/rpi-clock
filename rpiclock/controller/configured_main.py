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

"""Configuration-driven application main."""

from typing import Optional

from .configured_screen import ConfiguredScreen
from .main_controller import MainController


def main(config_path: str):
    """
    Main application loop.

    Extract screen data from the configuration and sets up the main controller
    to run the application.

    Does not return unless an exception happens.

    :param config_path: configuration file path
    """
    # Importing the panels package imports all the panel modules, which allows
    # decorated Panel classes to self-register.
    # noinspection PyUnresolvedReferences
    from rpiclock import panels
    controller = MainController(config_path)
    if not controller.config.screens:
        raise RuntimeError('No screens are configured.')
    initial_screen_name: Optional[str] = None
    for screen_name, screen_config in controller.config.screens.items():
        controller.add_screen(screen_name, ConfiguredScreen)
        if initial_screen_name is None:
            initial_screen_name = screen_name
    assert initial_screen_name
    controller.main(initial_screen_name)
