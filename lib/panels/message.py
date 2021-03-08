from typing import Optional

from ..event_manager import EventManager
from ..panel import Panel
from ..typing import Interval
from ..viewport import Viewport


class MessagePanel(Panel):

    def __init__(self):
        self.text = ''
        self.previous_text = ''
        self.duration: Optional[Interval] = None

    def set(self, text: str, duration: Interval = None):
        self.text = text
        self.duration = duration

    def on_initialize_events(self, event_manager: EventManager):
        pass

    def on_display(self, viewport: Viewport):
        viewport.text(self.text, duration=self.duration)
        self.previous_text = self.text

    def on_check(self) -> bool:
        return self.text != self.previous_text
