from .event_manager import EventManager
from .viewport import Viewport


class Panel:

    def on_initialize_events(self, event_manager: EventManager):
        raise NotImplementedError

    def on_display(self, viewport: Viewport):
        raise NotImplementedError

    def on_check(self) -> bool:
        raise NotImplementedError
