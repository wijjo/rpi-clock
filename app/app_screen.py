import sys
from typing import Optional

from lib import log
from lib.base_screen import BaseScreen
from lib.config import Config
from lib.display import Display
from lib.event_manager import EventManager
from lib.typing import Interval
from lib.viewport import Viewport
from lib.panels.message import MessagePanel


class AppScreen(BaseScreen):

    def __init__(self,
                 config: Config,
                 display: Display,
                 event_manager: EventManager):
        super().__init__(config, display, event_manager)
        # Viewport stubs get populated in on_create_viewports().
        self.body_viewport: Optional[Viewport] = None
        self.message_viewport: Optional[Viewport] = None
        self.message_panel: Optional[MessagePanel] = None

    def on_initialize_events(self):
        self.event_manager.register('button', self.on_button1, 1)
        self.event_manager.register('button', self.on_button2, 2)
        self.event_manager.register('button', self.on_button3, 3)
        # Button #4 is used for power (see /boot/config.txt).
        # self.event_manager.register('button', self.on_button4, 4)

    def on_create_viewports(self):
        log.info('Initialize base application screen.')
        outer_viewport = Viewport(self.display, self.display.rect)
        self.body_viewport, self.message_viewport = outer_viewport.vsplit(210)
        self.on_app_create_viewports(self.body_viewport)

    def on_configure_viewports(self):
        self.message_viewport.configure(font_size=self.config.message_font_size,
                                        color=self.config.message_color)
        self.on_app_configure_viewports()

    def on_create_panels(self):
        self.message_panel = MessagePanel()
        self.add_panel(self.message_viewport, self.message_panel)
        self.on_app_create_panels()

    def on_app_create_viewports(self, viewport: Viewport):
        raise NotImplementedError

    def on_app_configure_viewports(self):
        raise NotImplementedError

    def on_app_create_panels(self):
        raise NotImplementedError

    def on_button1(self):
        self.event_manager.send('trigger', 'screen', 'main')

    def on_button2(self):
        self.message('button2', duration=5)

    @staticmethod
    def on_button3():
        sys.exit(0)

    # def on_button4(self):
    #     self.message('button4', duration=5)

    def message(self, text: str, duration: Interval = None):
        log.info(f'message: {text}')
        self.message_panel.set(text, duration=duration)
