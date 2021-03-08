from typing import Optional

from lib import log
from lib.config import Config
from lib.display import Display
from lib.event_manager import EventManager
from lib.panels.time import TimePanel
from lib.panels.weather import WeatherPanel
from lib.viewport import Viewport

from .app_screen import AppScreen


class MainScreen(AppScreen):

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

    def on_app_create_viewports(self, viewport: Viewport):
        log.info('Initialize main screen.')
        (time_viewport,
         self.date_viewport,
         self.weather1_viewport,
         self.weather2_viewport) = viewport.vsplit(120, 30, 30)
        self.time1_viewport, self.time2_viewport = time_viewport.hsplit(260)

    def on_app_configure_viewports(self):
        self.time1_viewport.configure(fx=.5, fy=.5,
                                      font_size=self.config.time1_font_size,
                                      color=self.config.time1_color)
        self.time2_viewport.configure(fx=.5, fy=.5,
                                      font_size=self.config.time2_font_size,
                                      color=self.config.time2_color)
        self.date_viewport.configure(fx=.5, fy=1,
                                     font_size=self.config.date_font_size,
                                     color=self.config.date_color)
        self.weather1_viewport.configure(fx=.5, fy=1,
                                         font_size=self.config.weather1_font_size,
                                         color=self.config.weather1_color)
        self.weather2_viewport.configure(fx=.5, fy=1,
                                         font_size=self.config.weather2_font_size,
                                         color=self.config.weather2_color)

    def on_app_create_panels(self):
        self.add_panel(self.time1_viewport, TimePanel(self.config.time1_format))
        self.add_panel(self.time2_viewport, TimePanel(self.config.time2_format))
        self.add_panel(self.date_viewport, TimePanel(self.config.date_format))
        self.add_panel(self.weather1_viewport,
                       WeatherPanel(self.config.latitude,
                                    self.config.longitude,
                                    self.config.weather1_format,
                                    user_agent=self.config.user_agent))
        self.add_panel(self.weather2_viewport,
                       WeatherPanel(self.config.latitude,
                                    self.config.longitude,
                                    self.config.weather2_format,
                                    user_agent=self.config.user_agent))
