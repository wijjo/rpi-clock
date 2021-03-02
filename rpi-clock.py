#!/usr/bin/env python3

import os
import sys
import atexit
import logging

# Force running as root.
if os.getuid() != 0:
    os.execlp('sudo', 'sudo', *sys.argv)

from time import sleep, time, localtime, strftime
import RPi.GPIO as GPIO

from lib.panel import Panel
from lib.screen import Screen
from lib.timer import Timer

PID_FILE = '/tmp/rpi-clock.pid'

log = logging.getLogger(__name__)
out_hdlr = logging.StreamHandler(sys.stdout)
out_hdlr.setFormatter(logging.Formatter('%(asctime)s %(message)s'))
out_hdlr.setLevel(logging.DEBUG)
log.addHandler(out_hdlr)
log.setLevel(logging.DEBUG)

COLOR_BRIGHT = (120, 80, 40)
COLOR_NORMAL = (100, 60, 30)
COLOR_DIM = (80, 60, 30)


class Controller:

    default_text_color = Screen.white
    bg_default = Screen.black
    poll_interval = 0.1
    button_pins = [17, 22, 23, 27]

    def __init__(self):
        self.timers = []
        self.tick_handlers = []

        log.debug('Initialize GPIO.')
        GPIO.setmode(GPIO.BCM)
        self.button_handlers = []
        for pin in self.button_pins:
            GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            self.button_handlers.append([])

        log.debug('Configure screen and panels.')
        self.screen = Screen()
        top_panel, bottom_panel  = self.screen.panel.vsplit(y=150)
        time_panel, self.date_panel = top_panel.vsplit(y=130)
        self.time1_panel, self.time2_panel = time_panel.hsplit(x=260)
        self.time1_panel.configure(fx=.5, fy=.5, font_size=140, color=COLOR_BRIGHT)
        self.time2_panel.configure(fx=.5, fy=.5, font_size=70, color=COLOR_DIM)
        self.date_panel.configure(fx=.5, fy=1, font_size=36, color=COLOR_NORMAL)
        gap_panel, self.message_panel = bottom_panel.vsplit(y=60)
        self.message_panel.configure(fx=0, fy=1, color=COLOR_DIM)

        self.screen.clear()

    def add_button_handler(self, button_num, function):
        self.button_handlers[button_num - 1].append(function)

    def add_timer_handler(self, interval, function, max_count=None):
        self.timers.append(Timer(interval, function, max_count=max_count))

    def add_tick_handler(self, function):
        self.tick_handlers.append(function)

    def main(self):
        while True:
            for tick_function in self.tick_handlers:
                tick_function(self)
            for pin_idx, pin in enumerate(self.button_pins):
                if not GPIO.input(pin):
                    for button_handler in self.button_handlers[pin_idx]:
                        button_handler(self)
            time_now = time()
            active_timers = []
            for timer in self.timers:
                if timer.is_active() and timer.check(check_time=time_now):
                    timer.function(self)
                if timer.is_active():
                    active_timers.append(timer)
            self.timers = active_timers
            sleep(self.poll_interval)

    def message(self, text, bg_color=None, color=None, duration=None):
        log.info('message: %s' % text)
        self.message_panel.text(text)
        if duration is not None:
            def _clear(controller):
                controller.message_panel.clear()
            self.add_timer_handler(duration, _clear, max_count=1)


class Watcher:

    def __init__(self):
        self.local_time = None

    @classmethod
    def on_button1(cls, controller):
        controller.message('button1', duration=5)

    @classmethod
    def on_button2(cls, controller):
        controller.message('button2', duration=5)

    @classmethod
    def on_button3(cls, controller):
        controller.message('button3', duration=5)

    @classmethod
    def on_button4(cls, controller):
        controller.message('button4', duration=5)

    def on_tick(self, controller):
        local_time = localtime()
        if (self.local_time is None
                or local_time.tm_hour != self.local_time.tm_hour
                or local_time.tm_min != self.local_time.tm_min):
            controller.time1_panel.text('%02d:%02d' % (local_time.tm_hour, local_time.tm_min))
        if (self.local_time is None
                or local_time.tm_sec != self.local_time.tm_sec):
            controller.time2_panel.text('%02d' % local_time.tm_sec)
        if (self.local_time is None
                or local_time.tm_year != self.local_time.tm_year
                or local_time.tm_mon != self.local_time.tm_mon
                or local_time.tm_mday != self.local_time.tm_mday):
            controller.date_panel.text(strftime('%a %B %d %Y', local_time))
        self.local_time = local_time


def start():
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


def finish():
    if os.path.exists(PID_FILE):
        os.remove(PID_FILE)


def main():
    start()
    atexit.register(finish)
    log.info('Create watcher.')
    watcher = Watcher()
    log.info('Create controller.')
    controller = Controller()
    controller.add_button_handler(1, watcher.on_button1)
    controller.add_button_handler(2, watcher.on_button2)
    controller.add_button_handler(3, watcher.on_button3)
    controller.add_button_handler(4, watcher.on_button4)
    controller.add_tick_handler(watcher.on_tick)
    log.info('Start main loop.')
    controller.main()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        sys.stderr.write(os.linesep)
        sys.exit(2)
