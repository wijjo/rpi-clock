from typing import Optional

from . import log
from .event_manager import EventManager
from .panel import Panel
from .viewport import Viewport


class ScreenPanel:
    def __init__(self, viewport: Viewport, panel: Panel):
        self.viewport = viewport
        self.panel = panel


class ScreenManager:

    def __init__(self, event_manager: EventManager):
        self.event_manager = event_manager
        self.screens = {}
        self.current: Optional[str] = None

    def add_screen(self, name, screen):
        self.screens[name] = screen

    def show_screen(self, name):
        if name != self.current:
            self.event_manager.clear()
            if name in self.screens:
                self.screens[name].initialize()
                self.current = name
            else:
                log.error(f'Unable to show unknown screen name "{name}".')
                self.current = None
