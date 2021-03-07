from typing import Callable


class EventHandler:
    def __init__(self, function: Callable, permanent: bool):
        self.function = function
        self.permanent = permanent
