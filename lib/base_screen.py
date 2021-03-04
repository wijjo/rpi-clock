# TODO: This module should probably be broken up into an app and library component.
# E.g. the generic event, screen, and panel management should go in lib, but the
# specific screen panels, etc. should be in an app screen base class.

from typing import List

from .config import Config
from .display import Display
from .event_manager import EventManager
from .panel import Panel
from .screens import ScreenManager
from .viewport import Viewport


class ScreenPanel:
    def __init__(self, viewport: Viewport, panel: Panel):
        self.viewport = viewport
        self.panel = panel


class BaseScreen:

    def __init__(self,
                 config: Config,
                 display: Display,
                 event_manager: EventManager,
                 screen_manager: ScreenManager):
        self.config = config
        self.display = display
        self.event_manager = event_manager
        self.screen_manager = screen_manager
        self.screen_panels: List[ScreenPanel] = []

    def add_panel(self, viewport: Viewport, panel: Panel):
        self.screen_panels.append(ScreenPanel(viewport, panel))

    def initialize(self):
        """
        Base screen initialization.
        """
        self.on_initialize()
        self.event_manager.register('tick', self.on_tick)
        for screen_panel in self.screen_panels:
            screen_panel.panel.on_initialize(self.event_manager)
        for screen_panel in self.screen_panels:
            screen_panel.panel.on_display(screen_panel.viewport)

    def on_initialize(self):
        """
        Required hook for sub-class initialization.
        """
        raise NotImplementedError

    def on_tick(self):
        """
        Called to update panels.
        """
        for screen_panel in self.screen_panels:
            if screen_panel.panel.on_check():
                screen_panel.panel.on_display(screen_panel.viewport)
