from time import localtime, strftime

from lib.display import Display
from lib.events import EventManager
from lib.screens import ScreenManager

from . import COLOR_BRIGHT, COLOR_NORMAL, COLOR_DIM
from .base_screen import BaseScreen


class MainScreen(BaseScreen):

    default_text_color = Display.white
    bg_default = Display.black

    def __init__(self,
                 display: Display,
                 event_manager: EventManager,
                 screen_manager: ScreenManager):
        super().__init__(display, event_manager, screen_manager)
        # For checking when time/date updates are needed.
        self.local_time = None
        # Carve out panel viewports.
        time_panel, below_time_panel = self.body_panel.vsplit(y=120)
        self.date_panel, unused_panel = below_time_panel.vsplit(y=30)
        self.time1_panel, self.time2_panel = time_panel.hsplit(x=260)
        self.time1_panel.configure(fx=.5, fy=.5, font_size=140, color=COLOR_BRIGHT)
        self.time2_panel.configure(fx=.5, fy=.5, font_size=70, color=COLOR_DIM)
        self.date_panel.configure(fx=.5, fy=1, font_size=36, color=COLOR_NORMAL)

    def initialize(self):
        super().initialize()
        self.local_time = localtime()
        self.display_time1()
        self.display_time2()
        self.display_date()

    def display_time1(self):
        self.time1_panel.text(strftime('%H:%M', self.local_time))

    def display_time2(self):
        self.time2_panel.text(strftime('%S', self.local_time))

    def display_date(self):
        self.date_panel.text(strftime('%a %B %d %Y', self.local_time))

    def on_tick(self):
        local_time = localtime()
        hour_changed = local_time.tm_hour != self.local_time.tm_hour
        minute_changed = local_time.tm_min != self.local_time.tm_min
        second_changed = local_time.tm_sec != self.local_time.tm_sec
        year_changed = local_time.tm_year != self.local_time.tm_year
        month_changed = local_time.tm_mon != self.local_time.tm_mon
        day_changed = local_time.tm_mday != self.local_time.tm_mday
        self.local_time = local_time
        if hour_changed or minute_changed:
            self.display_time1()
        if second_changed:
            self.display_time2()
        if year_changed or month_changed or day_changed:
            self.display_date()
