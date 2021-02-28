#!/usr/bin/env python

import os
import sys
import atexit


# Force running as root.
if os.getuid() != 0:
    os.execlp('sudo', 'sudo', *sys.argv)

import pygame
from time import sleep, time, localtime
import RPi.GPIO as GPIO

PID_FILE = '/tmp/rpi-clock.pid'


class Screen:

    device = '/dev/fb1'
    size = (320, 240)
    center = (160, 120)

    white = (255, 255, 255)
    black = (0, 0, 0)
    grey = (128, 128, 128)
    red = (255, 0, 0)
    green = (0, 255, 0)
    blue = (0, 0, 255)

    def __init__(self):
        os.putenv('SDL_FBDEV', self.device)


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

    screen = Screen()

    heading_width = screen.size[0]
    heading_height = int(screen.size[1] / 2)
    heading_font_size = heading_height
    heading_rect = pygame.Rect(0, 0, heading_width, heading_height)

    message_width = int(screen.size[0] / 2)
    message_height = int(screen.size[1] / 8)
    message_font_size = message_height
    message_rect = pygame.Rect(screen.size[0] - message_width,
                               screen.size[1] - message_height,
                               message_width,
                               message_height)

    font_size_big = 100
    default_text_color = screen.white
    bg_default = screen.black
    poll_interval = 0.1
    button_pins = [17, 22, 23, 27]

    def __init__(self):
        GPIO.setmode(GPIO.BCM)
        self.button_handlers = []
        for pin in self.button_pins:
            GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            self.button_handlers.append([])
        pygame.init()
        self.font_big = pygame.font.Font(None, self.font_size_big)
        self.heading_font = pygame.font.Font(None, self.heading_font_size)
        self.message_font = pygame.font.Font(None, self.message_font_size)
        pygame.mouse.set_visible(False)
        self.surface = pygame.display.set_mode(self.screen.size)
        self.surface.fill(self.bg_default)
        self.timers = []
        self.tick_handlers = []
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

    def text_left(self, text, font, rect, color=None, bg_color=None):
        self.surface.fill(bg_color or self.screen.black, rect=rect)
        text_surface = font.render(text, True, color or self.default_text_color)
        self.surface.blit(text_surface, rect)
        pygame.display.update()

    def text_center(self, text, font, rect, color=None, bg_color=None):
        self.surface.fill(bg_color or self.screen.black, rect=rect)
        text_width, text_height = font.size(text)
        text_rect = pygame.Rect(rect.left + int((rect.width - text_width) / 2),
                                rect.top,
                                text_width,
                                text_height)
        text_surface = font.render(text, True, color or self.default_text_color)
        self.surface.blit(text_surface, text_rect)
        pygame.display.update()

    def text_right(self, text, font, rect, color=None, bg_color=None):
        self.surface.fill(bg_color or self.screen.black, rect=rect)
        text_width, text_height = font.size(text)
        text_rect = pygame.Rect(rect.left + rect.width - text_width,
                                rect.top,
                                text_width,
                                text_height)
        text_surface = font.render(text, True, color or self.default_text_color)
        self.surface.blit(text_surface, text_rect)
        pygame.display.update()

    def heading(self, text, bg_color=None, color=None):
        self.text_center(text, self.heading_font, self.heading_rect, color=color, bg_color=bg_color)

    def message(self, text, bg_color=None, color=None, duration=None):
        print('message: %s' % text)
        self.text_right(text, self.message_font, self.message_rect, color=color, bg_color=bg_color)
        if duration is not None:
            def _clear(_controller):
                print('clear message')
                self.surface.fill(bg_color or self.screen.black, rect=self.message_rect)
                pygame.display.update()
            self.add_timer_handler(duration, _clear, max_count=1)


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
            text = '%02d:%02d.%02d' % (local_time.tm_hour,
                                       local_time.tm_min,
                                       local_time.tm_sec)
            controller.heading(text, color=(50, 150, 150))
            self.local_time = local_time


def start():
    if os.path.exists(PID_FILE):
        with open(PID_FILE) as pid_file:
            pid = int(pid_file.read().strip())
            try:
                os.kill(pid, 2)
                print 'Killed previous run (PID=%d).' % pid
            except OSError:
                print 'Previous run (PID=%d) must have died.' % pid
        os.remove(PID_FILE)
    with open(PID_FILE, 'w') as pid_file:
        pid_file.write(str(os.getpid()))


def finish():
    if os.path.exists(PID_FILE):
        os.remove(PID_FILE)


def main():
    start()
    atexit.register(finish)
    print 'Creating watcher...'
    watcher = Watcher()
    controller = Controller()
    controller.add_button_handler(1, watcher.on_button1)
    controller.add_button_handler(2, watcher.on_button2)
    controller.add_button_handler(3, watcher.on_button3)
    controller.add_button_handler(4, watcher.on_button4)
    controller.add_tick_handler(watcher.on_tick)
    controller.main()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('')
        sys.exit(2)
