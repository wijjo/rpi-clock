from .event_handler import EventHandler


class EventProducer:

    def register(self, handler: EventHandler, *args, **kwargs):
        raise NotImplementedError

    def clear(self):
        raise NotImplementedError

    def tick(self):
        raise NotImplementedError

    def send(self, *args, **kwargs):
        raise NotImplementedError

    def display_name(self) -> str:
        raise NotImplementedError
