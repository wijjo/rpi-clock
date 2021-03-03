from typing import List

from lib import log
from lib.display import Display
from lib.events import EventManager
from lib.message_panel import MessagePanel
from lib.panel import Panel
from lib.screens import ScreenManager
from lib.typing import Duration
from lib.viewport import Viewport

from . import COLOR_DIM


class ScreenPanel:
    def __init__(self, viewport: Viewport, panel: Panel):
        self.viewport = viewport
        self.panel = panel


class BaseScreen:

    def __init__(self,
                 display: Display,
                 event_manager: EventManager,
                 screen_manager: ScreenManager):
        self.display = display
        self.event_manager = event_manager
        self.screen_manager = screen_manager
        self.screen_panels: List[ScreenPanel] = []
        # Provide sub-class with common viewport viewports for screen consistency.
        outer_viewport = Viewport(self.display, self.display.rect)
        self.body_viewport, message_viewport = outer_viewport.vsplit(210)
        message_viewport.configure(fx=0, fy=1, color=COLOR_DIM)
        self.message_panel = MessagePanel()
        self.add_panel(message_viewport, self.message_panel)

    def add_panel(self, viewport: Viewport, panel: Panel):
        self.screen_panels.append(ScreenPanel(viewport, panel))

    def initialize(self):
        """
        Base screen initialization.
        """
        self.event_manager.register('button', self.on_button1, 1)
        self.event_manager.register('button', self.on_button2, 2)
        self.event_manager.register('button', self.on_button3, 3)
        self.event_manager.register('button', self.on_button4, 4)
        self.event_manager.register('tick', self.on_tick)
        for screen_panel in self.screen_panels:
            screen_panel.panel.on_display(screen_panel.viewport)
        self.on_initialize()

    def message(self, text: str, duration: Duration = None):
        log.info(f'message: {text}')
        self.message_panel.set(text, duration=duration)

    def on_initialize(self):
        """
        Optional hook for sub-class initialization.
        """
        pass

    def on_button1(self):
        self.screen_manager.show_screen('main')

    def on_button2(self):
        self.message('button2', duration=5)

    def on_button3(self):
        self.message('button3', duration=5)

    def on_button4(self):
        self.message('button4', duration=5)

    def on_tick(self):
        """
        Called to update panels.
        """
        for screen_panel in self.screen_panels:
            if screen_panel.panel.on_check():
                screen_panel.panel.on_display(screen_panel.viewport)
