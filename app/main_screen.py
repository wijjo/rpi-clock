from typing import Optional

from lib import log
from lib.config import Config
from lib.display import Display
from lib.event_manager import EventManager
from lib.font_manager import FontManager
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
                 event_manager: EventManager,
                 font_manager: FontManager):
        super().__init__(config, display, event_manager, font_manager)
        # Viewport stubs get populated in on_app_create_viewports().
        self.time_viewport: Optional[Viewport] = None
        self.date_viewport: Optional[Viewport] = None
        self.seconds_viewport: Optional[Viewport] = None
        self.weather1_viewport: Optional[Viewport] = None
        self.weather2_viewport: Optional[Viewport] = None
        self.message_viewport: Optional[Viewport] = None
        self.message_panel: Optional[MessagePanel] = None
        self.weather_user_agent = f'({self.config.domain}, {self.config.email})'

    def on_initialize_events(self):
        self.event_manager.register('button', self.on_button1, 1)
        self.event_manager.register('button', self.on_button2, 2)

    def on_create_viewports(self):
        log.info('Create main screen viewports.')
        outer_viewport = Viewport(self.display, self.display.rect)
        rows = outer_viewport.vsplit(*self.config.rows)
        row1_columns = rows[0].hsplit(self.config.panels.time.width,
                                      self.config.panels.seconds.width)
        self.time_viewport = row1_columns[0]
        self.seconds_viewport = row1_columns[1]
        self.date_viewport = rows[1]
        self.weather1_viewport = rows[2]
        self.weather2_viewport = rows[3]
        self.message_viewport = rows[4]

    # noinspection DuplicatedCode
    def on_configure_viewports(self):
        log.info('Configure main screen viewports.')
        font_time = self.font_manager.get_font(self.config.fonts.time)
        font_text = self.font_manager.get_font(self.config.fonts.text)
        self.time_viewport.configure(fx=self.config.panels.time.fx,
                                     fy=self.config.panels.time.fy,
                                     font_name=font_time,
                                     font_size=self.config.panels.time.font_size,
                                     color=self.config.panels.time.color,
                                     bg_color=self.config.panels.time.bg_color,
                                     margins=self.config.panels.time.margins)
        self.seconds_viewport.configure(fx=self.config.panels.seconds.fx,
                                        fy=self.config.panels.seconds.fy,
                                        font_name=font_time,
                                        font_size=self.config.panels.seconds.font_size,
                                        color=self.config.panels.seconds.color,
                                        bg_color=self.config.panels.seconds.bg_color,
                                        margins=self.config.panels.seconds.margins)
        self.date_viewport.configure(fx=self.config.panels.date.fx,
                                     fy=self.config.panels.date.fy,
                                     font_name=font_text,
                                     font_size=self.config.panels.date.font_size,
                                     color=self.config.panels.date.color,
                                     bg_color=self.config.panels.date.bg_color,
                                     margins=self.config.panels.date.margins)
        self.weather1_viewport.configure(fx=self.config.panels.weather1.fx,
                                         fy=self.config.panels.weather1.fy,
                                         font_name=font_text,
                                         font_size=self.config.panels.weather1.font_size,
                                         color=self.config.panels.weather1.color,
                                         bg_color=self.config.panels.weather1.bg_color,
                                         margins=self.config.panels.weather1.margins)
        self.weather2_viewport.configure(fx=self.config.panels.weather2.fx,
                                         fy=self.config.panels.weather2.fy,
                                         font_name=font_text,
                                         font_size=self.config.panels.weather2.font_size,
                                         color=self.config.panels.weather2.color,
                                         bg_color=self.config.panels.weather2.bg_color,
                                         margins=self.config.panels.weather2.margins)
        self.message_viewport.configure(fx=self.config.panels.message.fx,
                                        fy=self.config.panels.message.fy,
                                        font_name=font_text,
                                        font_size=self.config.panels.message.font_size,
                                        color=self.config.panels.message.color,
                                        bg_color=self.config.panels.message.bg_color,
                                        margins=self.config.panels.message  .margins)

    def on_create_panels(self):
        log.info('Create main screen panels.')
        self.add_panel(self.time_viewport, TimePanel(self.config.panels.time.format))
        self.add_panel(self.seconds_viewport, TimePanel(self.config.panels.seconds.format))
        self.add_panel(self.date_viewport, TimePanel(self.config.panels.date.format))
        self.add_panel(self.weather1_viewport,
                       WeatherPanel(self.config.latitude,
                                    self.config.longitude,
                                    self.config.panels.weather1.format,
                                    user_agent=self.weather_user_agent))
        self.add_panel(self.weather2_viewport,
                       WeatherPanel(self.config.latitude,
                                    self.config.longitude,
                                    self.config.panels.weather2.format,
                                    user_agent=self.weather_user_agent))
        self.message_panel = MessagePanel()
        self.add_panel(self.message_viewport, self.message_panel)

    def message(self, text: str, duration: Interval = None):
        log.info(f'message: {text}')
        self.message_panel.set(text, duration=duration)

    def on_button1(self):
        self.event_manager.send('trigger', 'screen', 'main')

    def on_button2(self):
        self.message('button2', duration=5)
