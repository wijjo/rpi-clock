from time import time
from typing import Callable

from .timer import Timer
from .events import EventProducer


class TimerEvents(EventProducer):

    def __init__(self):
        self.timers = []

    def register(self, function: Callable, *args, **kwargs):
        duration = args[0]
        max_count = kwargs.pop('max_count', None)
        self.timers.append(Timer(duration, function, max_count=max_count))

    def tick(self):
        time_now = time()
        active_timers = []
        for timer in self.timers:
            if timer.is_active() and timer.check(check_time=time_now):
                timer.function()
            if timer.is_active():
                active_timers.append(timer)
        self.timers = active_timers
