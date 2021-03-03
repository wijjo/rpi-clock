from typing import Union

from lib import log
from lib.display import Display
from lib.events import EventManager
from lib.screens import ScreenManager

from . import COLOR_DIM


class BaseScreen:

    default_text_color = Display.white
    bg_default = Display.black

    def __init__(self,
                 display: Display,
                 event_manager: EventManager,
                 screen_manager: ScreenManager):
        self.local_time = None
        self.display = display
        self.event_manager = event_manager
        self.screen_manager = screen_manager
        # Provide sub-class with common panel viewports for screen consistency.
        self.body_panel, self.message_panel = display.panel.vsplit(y=210)
        self.message_panel.configure(fx=0, fy=1, color=COLOR_DIM)

    def initialize(self):
        """
        Sub-class must make sure to call super().initialize().
        """
        self.event_manager.register('button', self.on_button1, 1)
        self.event_manager.register('button', self.on_button2, 2)
        self.event_manager.register('button', self.on_button3, 3)
        self.event_manager.register('button', self.on_button4, 4)
        self.event_manager.register('tick', self.on_tick)

    def message(self, text: str, duration: Union[int, float] = None):
        log.info(f'message: {text}')
        self.message_panel.text(text, duration=duration)

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
        Hook for sub-class to receive tick events.
        """
        pass
