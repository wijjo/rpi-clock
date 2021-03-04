from typing import Callable


class EventProducer:

    def register(self, function: Callable, *args, **kwargs):
        raise NotImplementedError

    def clear(self):
        raise NotImplementedError

    def tick(self):
        raise NotImplementedError
