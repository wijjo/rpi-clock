from time import sleep

from .display import Display
from .events import EventManager
from .button_events import ButtonEvents
from .timer_events import TimerEvents
from .tick_events import TickEvents


class Controller:

    poll_interval = 0.1

    def __init__(self):
        self.event_manager = EventManager()
        self.event_manager.add_producer('button', ButtonEvents())
        self.event_manager.add_producer('timer', TimerEvents())
        self.event_manager.add_producer('tick', TickEvents())
        self.display = Display(self.event_manager)
        self.display.clear()
        self.screens = {}

    def add_screen(self, name, screen_class):
        self.screens[name] = screen_class(self.display, self.event_manager)

    def show_screen(self, name):
        self.screens[name].initialize()

    def main(self, initial_screen_name):
        self.show_screen(initial_screen_name)
        while True:
            self.event_manager.tick()
            sleep(self.poll_interval)
