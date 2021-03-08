from time import sleep

from . import log
from .config import Config
from .display import Display
from .event_manager import EventManager
from .events.button import ButtonEvents
from .events.timer import TimerEvents
from .events.tick import TickEvents
from .events.trigger import TriggerEvents
from .screens import ScreenManager

POLL_INTERVAL = 0.1
UPDATE_FREQUENCY = 60


class Controller:

    def __init__(self, config_path: str):
        self.config = Config(config_path)
        self.event_manager = EventManager()
        self.event_manager.add_producer('button', ButtonEvents())
        self.event_manager.add_producer('timer', TimerEvents())
        self.event_manager.add_producer('tick', TickEvents())
        self.event_manager.add_producer('trigger', TriggerEvents())
        self.event_manager.register('timer', self.update, UPDATE_FREQUENCY, permanent=True)
        self.event_manager.register('trigger', self.activate_screen, 'screen', permanent=True)
        self.screen_manager = ScreenManager(self.event_manager)
        self.display = Display(self.event_manager)
        self.display.clear()

    def add_screen(self, name, screen_class):
        self.screen_manager.add_screen(name, screen_class(self.config,
                                                          self.display,
                                                          self.event_manager))

    def update(self):
        if self.config.update():
            log.info('Reloaded configuration.')
            self.screen_manager.force_refresh()

    def activate_screen(self, screen_name: str):
        self.screen_manager.show_screen(screen_name)

    def main(self, initial_screen_name):
        self.screen_manager.show_screen(initial_screen_name)
        while True:
            self.event_manager.tick()
            sleep(POLL_INTERVAL)
