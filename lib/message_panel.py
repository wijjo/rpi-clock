from typing import Optional

from .panel import Panel
from .typing import Duration
from .viewport import Viewport


class MessagePanel(Panel):

    def __init__(self):
        self.text = ''
        self.previous_text = ''
        self.duration: Optional[Duration] = None

    def set(self, text: str, duration: Duration = None):
        self.text = text
        self.duration = duration

    def on_display(self, viewport: Viewport):
        viewport.text(self.text, duration=self.duration)
        self.previous_text = self.text

    def on_check(self) -> bool:
        return self.text != self.previous_text
