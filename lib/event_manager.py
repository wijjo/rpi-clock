from typing import Dict, Callable

from . import log
from .event_producer import EventProducer


class EventManager:

    def __init__(self):
        self.producers: Dict[str, EventProducer] = {}

    def clear(self):
        for event_producer in self.producers.values():
            event_producer.clear()

    def add_producer(self, name: str, producer: EventProducer):
        self.producers[name] = producer

    def register(self, producer_name: str, function: Callable, *args, **kwargs):
        if producer_name in self.producers:
            self.producers[producer_name].register(function, *args, **kwargs)
        else:
            log.error(f'Unable to register event for unknown producer "{producer_name}".')

    def tick(self):
        for event_producer in self.producers.values():
            event_producer.tick()
