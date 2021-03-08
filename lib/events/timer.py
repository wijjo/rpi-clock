from time import time
from typing import List

from .. import log
from ..event_handler import EventHandler
from ..event_producer import EventProducer
from ..timer import Timer


class TimerEvents(EventProducer):

    def __init__(self):
        self.permanent_timers: List[Timer] = []
        self.temporary_timers: List[Timer] = []

    def register(self, handler: EventHandler, *args, **kwargs):
        duration = args[0]
        max_count = kwargs.pop('max_count', None)
        timer = Timer(duration, handler.function, max_count=max_count)
        if handler.permanent:
            self.permanent_timers.append(timer)
        else:
            self.temporary_timers.append(timer)

    def tick(self):
        time_now = time()
        active_permanent_timers = []
        for timer in self.permanent_timers:
            if timer.is_active() and timer.check(check_time=time_now):
                timer.function()
            if timer.is_active():
                active_permanent_timers.append(timer)
        self.permanent_timers = active_permanent_timers
        active_temporary_timers = []
        for timer in self.temporary_timers:
            if timer.is_active() and timer.check(check_time=time_now):
                timer.function()
            if timer.is_active():
                active_temporary_timers.append(timer)
        self.temporary_timers = active_temporary_timers

    def clear(self):
        self.temporary_timers = []

    def send(self, *args, **kwargs):
        log.error('Timer event producer does not support send().')

    def display_name(self) -> str:
        handler_count = len(self.permanent_timers) + len(self.temporary_timers)
        return f'Timer[{handler_count} handlers]'
