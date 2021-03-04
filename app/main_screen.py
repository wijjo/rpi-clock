from lib.display import COLOR_BRIGHT, COLOR_NORMAL, COLOR_DIM
from lib.panels.time import TimePanel
from lib.panels.weather import WeatherPanel

from .app_screen import AppScreen


class MainScreen(AppScreen):

    def on_app_initialize(self):
        # Carve viewports out of the body viewport provided by the base class.
        (time_viewport,
         date_viewport,
         weather_viewport,
         empty_viewport) = self.body_viewport.vsplit(120, 30, 30)
        time1_viewport, time2_viewport = time_viewport.hsplit(260)
        # Customize viewports for display.
        time1_viewport.configure(fx=.5, fy=.5, font_size=140, color=COLOR_BRIGHT)
        time2_viewport.configure(fx=.5, fy=.5, font_size=70, color=COLOR_DIM)
        date_viewport.configure(fx=.5, fy=1, font_size=36, color=COLOR_NORMAL)
        weather_viewport.configure(fx=.5, fy=1, font_size=24, color=COLOR_NORMAL)
        # Register viewports/panels so that they get updated.
        self.add_panel(time1_viewport, TimePanel('%H:%M'))
        self.add_panel(time2_viewport, TimePanel('%S'))
        self.add_panel(date_viewport, TimePanel('%a %B %d %Y'))
        self.add_panel(weather_viewport, WeatherPanel(self.config.latitude,
                                                      self.config.longitude))
