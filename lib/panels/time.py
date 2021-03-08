from time import localtime, strftime
from typing import Optional

from ..event_manager import EventManager
from ..panel import Panel
from ..viewport import Viewport


class TimePanel(Panel):

    def __init__(self, time_format: str):
        def _check_format(*letters: str) -> bool:
            for letter in letters:
                if f'%{letter}' in time_format:
                    return True
            return False
        super().__init__()
        self.time_format = time_format
        self.use_year = _check_format('y', 'Y')
        self.use_month = _check_format('b', 'B', 'm')
        self.use_day = _check_format('d', 'a', 'A')
        self.use_hour = _check_format('H', 'I')
        self.use_minute = _check_format('M')
        self.use_second = _check_format('S')
        self.local_time: Optional[float] = None

    def on_initialize_events(self, event_manager: EventManager):
        pass

    def on_display(self, viewport: Viewport):
        if self.local_time is None:
            self.local_time = localtime()
        viewport.text(strftime(self.time_format, self.local_time))
        self.local_time = self.local_time

    def on_check(self) -> bool:
        t1 = self.local_time
        t2 = localtime()
        needs_display = (t1 is None
                         or (self.use_year and t1.tm_year != t2.tm_year)
                         or (self.use_month and t1.tm_mon != t2.tm_mon)
                         or (self.use_day and t1.tm_mday != t2.tm_mday)
                         or (self.use_hour and t1.tm_hour != t2.tm_hour)
                         or (self.use_minute and t1.tm_min != t2.tm_min)
                         or (self.use_second and t1.tm_sec != t2.tm_sec))
        self.local_time = t2
        return needs_display
