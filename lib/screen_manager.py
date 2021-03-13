from typing import Optional, Dict

from . import log
from .event_manager import EventManager
from .panel import Panel
from .screen import Screen
from .viewport import Viewport


class ScreenPanel:
    def __init__(self, viewport: Viewport, panel: Panel):
        self.viewport = viewport
        self.panel = panel


class ScreenManager:

    def __init__(self, event_manager: EventManager):
        self.event_manager = event_manager
        self.screens: Dict[str, Screen] = {}
        self.current: Optional[str] = None

    def add_screen(self, name, screen):
        self.screens[name] = screen

    def show_screen(self, name, outer_viewport: Viewport):
        if name != self.current:
            self.event_manager.clear()
            if name in self.screens:
                self.screens[name].initialize(outer_viewport)
                self.current = name
            else:
                log.error(f'Unable to show unknown screen name "{name}".')
                self.current = None

    @property
    def current_screen(self) -> Optional[Screen]:
        return self.screens.get(self.current)

    def force_refresh(self):
        if self.current is not None:
            log.info('Force screen refresh.')
            self.screens[self.current].refresh()
