import atexit
import os
import signal
import sys
from time import sleep

from . import log
from .config import Config
from .display import Display
from .event_manager import EventManager
from .events.button import ButtonEvents
from .events.timer import TimerEvents
from .events.tick import TickEvents
from .events.trigger import TriggerEvents
from .font_manager import FontManager
from .screen_manager import ScreenManager
from .viewport import Viewport

POLL_INTERVAL = 0.1


class Controller:

    instances = 0

    def __init__(self, config_path: str):
        assert self.instances == 0
        base_folder = os.path.dirname(config_path)
        self.instances += 1
        self.config = Config(config_path)
        self.event_manager = EventManager()
        self.event_manager.add_producer('button', ButtonEvents())
        self.event_manager.add_producer('timer', TimerEvents())
        self.event_manager.add_producer('tick', TickEvents())
        self.event_manager.add_producer('trigger', TriggerEvents())
        # Event handlers must be flagged permanent in order to survive screen initialization.
        self.event_manager.register('timer', self.update, self.config.update_interval,
                                    permanent=True)
        self.event_manager.register('trigger', self.activate_screen, 'screen', permanent=True)
        self.event_manager.register('button', self.on_button3, 3, permanent=True)
        self.event_manager.register('button', self.on_button4, 4, permanent=True)
        self.font_manager = FontManager(os.path.join(base_folder, 'fonts'))
        self.screen_manager = ScreenManager(self.event_manager)
        self.display = Display(self.event_manager)
        self.display.clear()
        self.outer_viewport = Viewport(self.display, self.display.rect)
        atexit.register(self.cleanup)

        def _signal_handler(signum, _frame):
            sys.exit(signum)

        signal.signal(signal.SIGTERM, _signal_handler)

    def add_screen(self, name, screen_class):
        self.screen_manager.add_screen(name, screen_class(self.config,
                                                          self.event_manager,
                                                          self.font_manager))

    def update(self):
        if self.config.update():
            log.info('Reloaded configuration.')
            self.screen_manager.force_refresh()

    def activate_screen(self, screen_name: str):
        self.screen_manager.show_screen(screen_name, self.outer_viewport)

    def on_button3(self):
        self.screen_manager.current_screen.message('Exiting...')
        sleep(2)
        sys.exit(0)

    def on_button4(self):
        self.screen_manager.current_screen.message('Powering off...')
        sleep(2)
        os.execlp('sudo', 'sudo', 'poweroff')

    def cleanup(self):
        log.info('Cleaning up...')
        self.display.shut_down()

    def main(self, initial_screen_name):
        self.screen_manager.show_screen(initial_screen_name, self.outer_viewport)
        while True:
            self.event_manager.tick()
            sleep(POLL_INTERVAL)
