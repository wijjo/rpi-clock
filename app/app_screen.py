from lib import log
from lib.base_screen import BaseScreen
from lib.config import Config
from lib.display import Display, COLOR_DIM
from lib.event_manager import EventManager
from lib.screens import ScreenManager
from lib.typing import Duration
from lib.viewport import Viewport
from lib.panels.message import MessagePanel


class AppScreen(BaseScreen):

    def __init__(self,
                 config: Config,
                 display: Display,
                 event_manager: EventManager,
                 screen_manager: ScreenManager):
        super().__init__(config, display, event_manager, screen_manager)
        # Provide sub-class with common viewport viewports for screen consistency.
        outer_viewport = Viewport(self.display, self.display.rect)
        self.body_viewport, message_viewport = outer_viewport.vsplit(210)
        message_viewport.configure(fx=0, fy=1, color=COLOR_DIM)
        self.message_panel = MessagePanel()
        self.add_panel(message_viewport, self.message_panel)

    def on_initialize(self):
        self.event_manager.register('button', self.on_button1, 1)
        self.event_manager.register('button', self.on_button2, 2)
        self.event_manager.register('button', self.on_button3, 3)
        self.event_manager.register('button', self.on_button4, 4)
        self.on_app_initialize()

    def on_app_initialize(self):
        raise NotImplementedError

    def on_button1(self):
        self.screen_manager.show_screen('main')

    def on_button2(self):
        self.message('button2', duration=5)

    def on_button3(self):
        self.message('button3', duration=5)

    def on_button4(self):
        self.message('button4', duration=5)

    def message(self, text: str, duration: Duration = None):
        log.info(f'message: {text}')
        self.message_panel.set(text, duration=duration)
