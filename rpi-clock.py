#!/usr/bin/env python

import os
import sys
import atexit
import logging


# Force running as root.
if os.getuid() != 0:
    os.execlp('sudo', 'sudo', *sys.argv)

import pygame
from time import sleep, time, localtime
import RPi.GPIO as GPIO

PID_FILE = '/tmp/rpi-clock.pid'

log = logging.getLogger(__name__)
out_hdlr = logging.StreamHandler(sys.stdout)
out_hdlr.setFormatter(logging.Formatter('%(asctime)s %(message)s'))
out_hdlr.setLevel(logging.DEBUG)
log.addHandler(out_hdlr)
log.setLevel(logging.DEBUG)


def calculate_sub_rect(outer_rect, x, y, w, h):
    """Calculate sub-rect of outer rect using x, y, w, h values between 0 and 1."""
    width = w * outer_rect.width
    height = h * outer_rect.height
    left = outer_rect.left + (x * outer_rect.width) - (width * x)
    top = outer_rect.top + (y * outer_rect.height) - (height * y)
    if width < 0 or width > outer_rect.width:
        width = outer_rect.width
    if height < 0 or height > outer_rect.height:
        height = outer_rect.height
    if left < outer_rect.left:
        left = outer_rect.left
    if left + width > outer_rect.left + outer_rect.width:
        left = outer_rect.width + outer_rect.width - width
    if top < outer_rect.height:
        top = outer_rect.height
    if top + height > outer_rect.top + outer_rect.height:
        top = outer_rect.top + outer_rect.height - height
    return pygame.Rect(int(left), int(top), int(width), int(height))


class Screen:

    device = '/dev/fb1'
    size = (320, 240)
    center = (160, 120)
    rect = pygame.Rect(0, 0, size[0], size[1])

    white = (255, 255, 255)
    black = (0, 0, 0)
    grey = (128, 128, 128)
    red = (255, 0, 0)
    green = (0, 255, 0)
    blue = (0, 0, 255)

    font_size_medium = 50
    font_size_large = 100

    def __init__(self, bg_color=None):
        os.putenv('SDL_FBDEV', self.device)
        self.bg_color = bg_color or self.black
        self.surface = pygame.display.set_mode(self.size)

    def clear(self):
        self.surface.fill(self.bg_color)
        pygame.display.update()

    def sub_rect(self, x, y, w, h):
        return calculate_sub_rect(self.rect, x, y, w, h)

    class Panel:

        def __init__(self, screen, rect, pos_x, pos_y, color, bg_color):
            self.screen = screen
            self.rect = rect
            self.pos_x = pos_x
            self.pos_y = pos_y
            self.color = color
            self.bg_color = bg_color
            self.font = pygame.font.Font(None, self.rect.height)

        def clear(self):
            self.screen.surface.fill(self.bg_color, rect=self.rect)

        def text(self, text):
            self.clear()
            text_width, text_height = self.font.size(text)
            text_rect = calculate_sub_rect(self.rect,
                                           self.pos_x,
                                           self.pos_y,
                                           text_width / self.rect.width,
                                           text_height / self.rect.height)
            text_surface = self.font.render(text, True, self.color)
            self.screen.surface.blit(text_surface, text_rect)
            pygame.display.update()

    def panel(self, x=0, y=0, w=1, h=1, pos_x=.5, pos_y=.5, color=None, bg_color=None):
        return self.Panel(self,
                          self.sub_rect(x, y, w, h),
                          pos_x,
                          pos_y,
                          color or self.white,
                          bg_color or self.bg_color)


class Timer:

    def __init__(self, interval, function, max_count=None):
        self.interval = interval
        self.function = function
        # max_count can be a countdown quantity or None for infinite.
        self.max_count = max_count
        self._count = 0
        # timed event is inactive when _next_time is None.
        self._next_time = time() + self.interval

    def check(self, check_time=None):
        if self._next_time is None:
            return False
        time_to_check = check_time or time()
        if time_to_check < self._next_time:
            return False
        self._count += 1
        if self._count < self.max_count:
            self._next_time = time_to_check + self.interval
        else:
            self._next_time = None
        return True

    def is_active(self):
        return self._next_time is not None


class Controller:

    default_text_color = Screen.white
    bg_default = Screen.black
    poll_interval = 0.1
    button_pins = [17, 22, 23, 27]

    def __init__(self):
        self.timers = []
        self.tick_handlers = []

        self.screen = Screen()

	log.debug('Initialize GPIO.')
        GPIO.setmode(GPIO.BCM)
        self.button_handlers = []
        for pin in self.button_pins:
            GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            self.button_handlers.append([])

	log.debug('Initialize PyGame.')
        pygame.init()
        pygame.mouse.set_visible(False)

        log.debug('Configure panels.')
        self.time1_panel = self.screen.panel(x=0, y=0, w=.7, h=.4, pos_x=.5, pos_y=.5, color=(120, 80, 40))
        self.time2_panel = self.screen.panel(x=1, y=0, w=.7, h=.2, pos_x=1, pos_y=1, color=(120, 80, 40))
        self.message_panel = self.screen.panel(x=0, y=1, w=1, h=.2, pos_x=0, pos_y=1, color=(100, 80, 60))

	log.debug('Clear screen.')
        self.screen.clear()

	log.info('Initial display update.')
        pygame.display.update()

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
            self.add_timer_handler(duration, self.message_panel.clear, max_count=1)


class Watcher:

    def __init__(self):
        self.local_time = localtime()

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
        if local_time != self.local_time:
            controller.time1_panel.text('%02d:%02d' % (local_time.tm_hour, local_time.tm_min))
            controller.time2_panel.text('%02d' % local_time.tm_sec)
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
