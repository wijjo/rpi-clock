from typing import Optional

from lib import log
from lib.config import Config
from lib.display import Display
from lib.event_manager import EventManager
from lib.panels.message import MessagePanel
from lib.panels.time import TimePanel
from lib.panels.weather import WeatherPanel
from lib.screen import Screen
from lib.typing import Interval
from lib.viewport import Viewport


class MainScreen(Screen):

    def __init__(self,
                 config: Config,
                 display: Display,
                 event_manager: EventManager):
        super().__init__(config, display, event_manager)
        # Viewport stubs get populated in on_app_create_viewports().
        self.time1_viewport: Optional[Viewport] = None
        self.time2_viewport: Optional[Viewport] = None
        self.date_viewport: Optional[Viewport] = None
        self.weather1_viewport: Optional[Viewport] = None
        self.weather2_viewport: Optional[Viewport] = None
        self.message_viewport: Optional[Viewport] = None
        self.message_panel: Optional[MessagePanel] = None

    def on_initialize_events(self):
        self.event_manager.register('button', self.on_button1, 1)
        self.event_manager.register('button', self.on_button2, 2)

    def on_create_viewports(self):
        log.info('Create main screen viewports.')
        outer_viewport = Viewport(self.display, self.display.rect)
        rows = outer_viewport.vsplit(*self.config.rows)
        time_columns = rows[0].hsplit(self.config.panels.time1.width,
                                      self.config.panels.time2.width)
        self.time1_viewport = time_columns[0]
        self.time2_viewport = time_columns[1]
        self.date_viewport = rows[1]
        self.weather1_viewport = rows[2]
        self.weather2_viewport = rows[3]
        self.message_viewport = self.weather2_viewport.overlay()

    def on_configure_viewports(self):
        log.info('Configure main screen panels.')
        self.time1_viewport.configure(fx=.5, fy=.5,
                                      font_size=self.config.panels.time1.font_size,
                                      color=self.config.panels.time1.color)
        self.time2_viewport.configure(fx=.5, fy=.5,
                                      font_size=self.config.panels.time2.font_size,
                                      color=self.config.panels.time2.color)
        self.date_viewport.configure(fx=.5, fy=1,
                                     font_size=self.config.panels.date.font_size,
                                     color=self.config.panels.date.color)
        self.weather1_viewport.configure(fx=.5, fy=1,
                                         font_size=self.config.panels.weather1.font_size,
                                         color=self.config.panels.weather1.color)
        self.weather2_viewport.configure(fx=.5, fy=1,
                                         font_size=self.config.panels.weather2.font_size,
                                         color=self.config.panels.weather2.color)
        self.message_viewport.configure(font_size=self.config.panels.message.font_size,
                                        color=self.config.panels.message.color)

    def on_create_panels(self):
        log.info('Create main screen panels.')
        self.add_panel(self.time1_viewport, TimePanel(self.config.panels.time1.format))
        self.add_panel(self.time2_viewport, TimePanel(self.config.panels.time2.format))
        self.add_panel(self.date_viewport, TimePanel(self.config.panels.date.format))
        self.add_panel(self.weather1_viewport,
                       WeatherPanel(self.config.latitude,
                                    self.config.longitude,
                                    self.config.panels.weather1.format,
                                    user_agent=self.config.user_agent))
        self.add_panel(self.weather2_viewport,
                       WeatherPanel(self.config.latitude,
                                    self.config.longitude,
                                    self.config.panels.weather2.format,
                                    user_agent=self.config.user_agent))
        self.message_panel = MessagePanel()
        self.add_panel(self.message_viewport, self.message_panel)

    def message(self, text: str, duration: Interval = None):
        log.info(f'message: {text}')
        self.message_panel.set(text, duration=duration)

    def on_button1(self):
        self.event_manager.send('trigger', 'screen', 'main')

    def on_button2(self):
        self.message('button2', duration=5)
