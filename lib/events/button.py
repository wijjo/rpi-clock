from RPi import GPIO
from typing import List, Optional

from lib import log
from ..event_handler import EventHandler
from ..event_producer import EventProducer


class ButtonEvents(EventProducer):

    # Reserve button #4 for power (/boot/config.txt).
    # button_pins = [17, 22, 23, 27]
    button_pins = [17, 22, 23]

    def __init__(self):
        self.button_handlers: List[Optional[EventHandler]] = [None] * len(self.button_pins)
        log.debug('Initialize GPIO.')
        GPIO.setmode(GPIO.BCM)
        for pin in self.button_pins:
            GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    def register(self, handler: EventHandler, *args, **kwargs):
        self.button_handlers[args[0] - 1] = handler

    def tick(self):
        for pin_idx, pin in enumerate(self.button_pins):
            if not GPIO.input(pin):
                if self.button_handlers[pin_idx] is not None:
                    self.button_handlers[pin_idx].function()

    def clear(self):
        for pin_idx, pin in enumerate(self.button_pins):
            if (self.button_handlers[pin_idx] is not None
                    and not self.button_handlers[pin_idx].permanent):
                self.button_handlers[pin_idx] = None

    def send(self, *args, **kwargs):
        log.error('Button event producer does not support send().')
