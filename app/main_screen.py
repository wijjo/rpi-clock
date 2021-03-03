from lib.display import Display
from lib.events import EventManager
from lib.screens import ScreenManager
from lib.time_panel import TimePanel

from . import COLOR_BRIGHT, COLOR_NORMAL, COLOR_DIM
from .base_screen import BaseScreen


class MainScreen(BaseScreen):

    def __init__(self,
                 display: Display,
                 event_manager: EventManager,
                 screen_manager: ScreenManager):
        super().__init__(display, event_manager, screen_manager)
        # Carve viewports out of the body viewport provided by the base class.
        time_viewport, date_viewport, empty_viewport = self.body_viewport.vsplit(120, 30)
        time1_viewport, time2_viewport = time_viewport.hsplit(260)
        # Customize viewports for display.
        time1_viewport.configure(fx=.5, fy=.5, font_size=140, color=COLOR_BRIGHT)
        time2_viewport.configure(fx=.5, fy=.5, font_size=70, color=COLOR_DIM)
        date_viewport.configure(fx=.5, fy=1, font_size=36, color=COLOR_NORMAL)
        # Register viewports/panels so that they get updated.
        self.add_panel(time1_viewport, TimePanel('%H:%M'))
        self.add_panel(time2_viewport, TimePanel('%S'))
        self.add_panel(date_viewport, TimePanel('%a %B %d %Y'))
