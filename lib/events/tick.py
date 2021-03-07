from typing import List, Callable

from .. import log
from ..event_handler import EventHandler
from ..event_producer import EventProducer


class TickEvents(EventProducer):

    def __init__(self):
        self.permanent_tick_handlers: List[Callable] = []
        self.temporary_tick_handlers: List[Callable] = []

    def register(self, handler: EventHandler, *args, **kwargs):
        if handler.permanent:
            self.permanent_tick_handlers.append(handler.function)
        else:
            self.temporary_tick_handlers.append(handler.function)

    def tick(self):
        for tick_function in self.temporary_tick_handlers + self.permanent_tick_handlers:
            tick_function()

    def clear(self):
        self.temporary_tick_handlers = []

    def send(self, *args, **kwargs):
        log.error('Tick event producer does not support send().')
