#!/usr/bin/env python3

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

import os
import sys

# Require running as root.
if os.getuid() != 0:
    sys.stderr.write('ERROR: This script must be run as root, e.g. using sudo.\n')
    sys.exit(1)

from lib import log
from lib.controller import Controller

from app.main_screen import MainScreen

CONFIG_PATH = os.path.join(os.path.dirname(__file__), 'config.json')


def main():
    """Main creates controller with a screen and then starts the controller."""
    log.info(f'Running rpi-clock as PID {os.getpid()}.')
    log.info('Create controller.')
    controller = Controller(CONFIG_PATH)
    log.info('Create main screen.')
    controller.add_screen('main', MainScreen)
    log.info('Start main loop.')
    controller.main('main')


if __name__ == '__main__':
    # Handle Control-C exception cleanly.
    try:
        main()
    except KeyboardInterrupt:
        sys.stderr.write(os.linesep)
        sys.exit(2)
