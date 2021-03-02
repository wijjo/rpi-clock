#!/usr/bin/env python3

import os
import sys
import atexit

from lib import log
from lib.controller import Controller

from app import PID_FILE
from app.main_screen import MainScreen

# Force running as root.
if os.getuid() != 0:
    os.execlp('sudo', 'sudo', *sys.argv)


def before_hook():
    if os.path.exists(PID_FILE):
        with open(PID_FILE) as pid_file:
            pid = int(pid_file.read().strip())
            try:
                os.kill(pid, 2)
                log.info('Killed previous run (PID=%d).' % pid)
            except OSError:
                log.info('Previous run (PID=%d) must have died.' % pid)
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
    controller = Controller()
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
