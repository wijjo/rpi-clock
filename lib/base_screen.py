from typing import List

from .config import Config
from .display import Display
from .event_manager import EventManager
from .panel import Panel
from .viewport import Viewport


class ScreenPanel:
    def __init__(self, viewport: Viewport, panel: Panel):
        self.viewport = viewport
        self.panel = panel


class BaseScreen:

    def __init__(self,
                 config: Config,
                 display: Display,
                 event_manager: EventManager):
        self.config = config
        self.display = display
        self.event_manager = event_manager
        self.screen_panels: List[ScreenPanel] = []

    def add_panel(self, viewport: Viewport, panel: Panel):
        self.screen_panels.append(ScreenPanel(viewport, panel))

    def initialize(self):
        """
        Base screen initialization.
        """
        self.on_initialize_events()
        self.event_manager.register('tick', self.on_tick)
        self.refresh()

    def refresh(self):
        """
        Refresh screen.
        """
        self.on_initialize_display()
        for screen_panel in self.screen_panels:
            screen_panel.panel.on_initialize(self.event_manager)
        self.display_panels(force=True)

    def display_panels(self, force=False):
        for screen_panel in self.screen_panels:
            if force or screen_panel.panel.on_check():
                screen_panel.panel.on_display(screen_panel.viewport)

    def on_initialize_events(self):
        """
        Required hook for sub-class event initialization.
        """
        raise NotImplementedError

    def on_initialize_display(self):
        """
        Required hook for sub-class display initialization.
        """
        raise NotImplementedError

    def on_tick(self):
        """
        Called to update panels.
        """
        self.display_panels()
