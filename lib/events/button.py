from RPi import GPIO
from typing import List, Callable

from lib import log
from ..event_producer import EventProducer


class ButtonEvents(EventProducer):

    button_pins = [17, 22, 23, 27]

    def __init__(self):
        self.button_handlers: List[List[Callable]] = []
        log.debug('Initialize GPIO.')
        GPIO.setmode(GPIO.BCM)
        for pin in self.button_pins:
            GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        self._clear_handlers()

    def _clear_handlers(self):
        self.button_handlers: List[List[Callable]] = [[], [], [], []]

    def register(self, function: Callable, *args, **kwargs):
        self.button_handlers[args[0] - 1].append(function)

    def tick(self):
        for pin_idx, pin in enumerate(self.button_pins):
            if not GPIO.input(pin):
                for button_handler in self.button_handlers[pin_idx]:
                    button_handler()

    def clear(self):
        self._clear_handlers()
