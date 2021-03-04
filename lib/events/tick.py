from typing import List, Callable

from ..event_producer import EventProducer


class TickEvents(EventProducer):

    def __init__(self):
        self.tick_handlers: List[Callable] = []

    def register(self, function: Callable, *args, **kwargs):
        self.tick_handlers.append(function)

    def tick(self):
        for tick_function in self.tick_handlers:
            tick_function()

    def clear(self):
        self.tick_handlers = []
