from typing import Dict, Callable

from . import log
from .event_handler import EventHandler
from .event_producer import EventProducer


class EventManager:

    def __init__(self):
        self.producers: Dict[str, EventProducer] = {}

    def clear(self):
        for event_producer in self.producers.values():
            event_producer.clear()

    def add_producer(self, producer_name: str, producer: EventProducer):
        self.producers[producer_name] = producer

    def register(self, producer_name: str, function: Callable, *args, **kwargs):
        handler = EventHandler(function, kwargs.pop('permanent', False))
        if producer_name in self.producers:
            self.producers[producer_name].register(handler, *args, **kwargs)
        else:
            log.error(f'Unable to register event for unknown producer "{producer_name}".')

    def send(self, producer_name: str, *args, **kwargs):
        """
        Send data to an event producer.

        Not all producers will support or do anything with this.

        :param producer_name: producer name
        :param args: positional arguments to send
        :param kwargs: keyword arguments to send
        """
        if producer_name in self.producers:
            self.producers[producer_name].send(*args, **kwargs)
        else:
            log.error(f'Unable to send data to unknown producer "{producer_name}".')

    def tick(self):
        for event_producer in self.producers.values():
            event_producer.tick()
