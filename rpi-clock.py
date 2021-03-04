#!/usr/bin/env python3

import os
import sys

# Force running as root.
if os.getuid() != 0:
    print('(force run as root)')
    os.execlp('sudo', 'sudo', *sys.argv)

import atexit

from lib import log
from lib.config import Config
from lib.controller import Controller

from app import PID_FILE
from app.main_screen import MainScreen

CONFIG_PATH = os.path.join(os.path.dirname(__file__), 'config.json')


def before_hook():
    if os.path.exists(PID_FILE):
        with open(PID_FILE) as pid_file:
            pid = int(pid_file.read().strip())
            try:
                os.kill(pid, 2)
                log.info(f'Killed previous run (PID={pid}).')
            except OSError:
                log.info(f'Previous run (PID={pid}) must have died.')
        os.remove(PID_FILE)
    with open(PID_FILE, 'w') as pid_file:
        pid_file.write(str(os.getpid()))


def after_hook():
    if os.path.exists(PID_FILE):
        os.remove(PID_FILE)


def main():
    before_hook()
    atexit.register(after_hook)
    log.info('Create controller.')
    config = Config(CONFIG_PATH)
    controller = Controller(config)
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
