from lib import log
from lib.panels.time import TimePanel
from lib.panels.weather import WeatherPanel
from lib.viewport import Viewport

from .app_screen import AppScreen


class MainScreen(AppScreen):

    def on_initialize_app_display(self, viewport: Viewport):
        log.info('Initialize main screen.')
        # Carve viewports out of the body viewport provided by the base class.
        (time_viewport,
         date_viewport,
         weather1_viewport,
         weather2_viewport) = viewport.vsplit(120, 30, 30)
        time1_viewport, time2_viewport = time_viewport.hsplit(260)
        # Customize viewports for display.
        time1_viewport.configure(fx=.5, fy=.5,
                                 font_size=self.config.time1_font_size,
                                 color=self.config.time1_color)
        time2_viewport.configure(fx=.5, fy=.5,
                                 font_size=self.config.time2_font_size,
                                 color=self.config.time2_color)
        date_viewport.configure(fx=.5, fy=1,
                                font_size=self.config.date_font_size,
                                color=self.config.date_color)
        weather1_viewport.configure(fx=.5, fy=1,
                                    font_size=self.config.weather1_font_size,
                                    color=self.config.weather1_color)
        weather2_viewport.configure(fx=.5, fy=1,
                                    font_size=self.config.weather2_font_size,
                                    color=self.config.weather2_color)
        # Configure the color of the parent AppScreen class' message viewport.
        self.message_viewport.configure(font_size=self.config.message_font_size,
                                        color=self.config.message_color)
        # Register viewports/panels so that they get updated.
        self.add_panel(time1_viewport, TimePanel(self.config.time1_format))
        self.add_panel(time2_viewport, TimePanel(self.config.time2_format))
        self.add_panel(date_viewport, TimePanel(self.config.date_format))
        self.add_panel(weather1_viewport, WeatherPanel(self.config.latitude,
                                                       self.config.longitude,
                                                       self.config.weather1_format,
                                                       user_agent=self.config.user_agent))
        self.add_panel(weather2_viewport, WeatherPanel(self.config.latitude,
                                                       self.config.longitude,
                                                       self.config.weather2_format,
                                                       user_agent=self.config.user_agent))
