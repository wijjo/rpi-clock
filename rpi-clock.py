#!/usr/bin/env python3

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
    log.info(f'Running rpi-clock as PID {os.getpid()}.')
    log.info('Create controller.')
    controller = Controller(CONFIG_PATH)
    log.info('Create main screen.')
    controller.add_screen('main', MainScreen)
    log.info('Start main loop.')
    controller.main('main')


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        sys.stderr.write(os.linesep)
        sys.exit(2)
