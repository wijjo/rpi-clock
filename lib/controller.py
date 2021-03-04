from time import sleep

from .config import Config
from .display import Display
from .event_manager import EventManager
from lib.events.button import ButtonEvents
from lib.events.timer import TimerEvents
from lib.events.tick import TickEvents
from .screens import ScreenManager


class Controller:

    poll_interval = 0.1

    def __init__(self, config: Config):
        self.config = config
        self.event_manager = EventManager()
        self.event_manager.add_producer('button', ButtonEvents())
        self.event_manager.add_producer('timer', TimerEvents())
        self.event_manager.add_producer('tick', TickEvents())
        self.screen_manager = ScreenManager(self.event_manager)
        self.display = Display(self.event_manager)
        self.display.clear()

    def add_screen(self, name, screen_class):
        self.screen_manager.add_screen(name, screen_class(self.config,
                                                          self.display,
                                                          self.event_manager,
                                                          self.screen_manager))

    def main(self, initial_screen_name):
        self.screen_manager.show_screen(initial_screen_name)
        while True:
            self.event_manager.tick()
            sleep(self.poll_interval)
