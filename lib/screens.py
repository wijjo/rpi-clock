from . import log
from .events import EventManager


class ScreenManager:

    def __init__(self, event_manager: EventManager):
        self.event_manager = event_manager
        self.screens = {}

    def add_screen(self, name, screen):
        self.screens[name] = screen

    def show_screen(self, name):
        self.event_manager.clear()
        if name in self.screens:
            self.screens[name].initialize()
        else:
            log.error(f'Unable to show unknown screen name "{name}".')
