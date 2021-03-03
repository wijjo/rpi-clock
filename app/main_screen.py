from time import localtime, strftime
from typing import Union

from lib import log
from lib.display import Display
from lib.events import EventManager
from lib.screens import ScreenManager

from . import COLOR_BRIGHT, COLOR_NORMAL, COLOR_DIM


class MainScreen:

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

        # Initialize panels.
        top_panel, bottom_panel = display.panel.vsplit(y=150)
        time_panel, self.date_panel = top_panel.vsplit(y=120)
        self.time1_panel, self.time2_panel = time_panel.hsplit(x=260)
        self.time1_panel.configure(fx=.5, fy=.5, font_size=140, color=COLOR_BRIGHT)
        self.time2_panel.configure(fx=.5, fy=.5, font_size=70, color=COLOR_DIM)
        self.date_panel.configure(fx=.5, fy=1, font_size=36, color=COLOR_NORMAL)
        gap_panel, self.message_panel = bottom_panel.vsplit(y=60)
        self.message_panel.configure(fx=0, fy=1, color=COLOR_DIM)

    def initialize(self):
        self.event_manager.register('button', self.on_button1, 1)
        self.event_manager.register('button', self.on_button2, 2)
        self.event_manager.register('button', self.on_button3, 3)
        self.event_manager.register('button', self.on_button4, 4)
        self.event_manager.register('tick', self.on_tick)
        self.local_time = localtime()
        self.display_time1()
        self.display_time2()
        self.display_date()

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
