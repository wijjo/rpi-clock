from typing import Dict, List, Callable

from .. import log
from ..event_handler import EventHandler
from ..event_producer import EventProducer


class TriggerEvent:
    def __init__(self, function: Callable, args: list, kwargs: dict):
        self.function = function
        self.args = args
        self.kwargs = kwargs


class TriggerEvents(EventProducer):
    """The trigger event producer supports manually-generated named events."""

    def __init__(self):
        self.permanent_handlers: Dict[str, Callable] = {}
        self.temporary_handlers: Dict[str, Callable] = {}
        self.triggers: List[TriggerEvent] = []

    def register(self, handler: EventHandler, *args, **kwargs):
        trigger_name = args[0]
        if handler.permanent:
            self.permanent_handlers[trigger_name] = handler.function
        else:
            self.temporary_handlers[trigger_name] = handler.function

    def tick(self):
        for trigger in self.triggers:
            trigger.function(*trigger.args, **trigger.kwargs)
        self.triggers = []

    def clear(self):
        self.temporary_handlers = {}
        self.triggers = []

    def send(self, *args, **kwargs):
        trigger_name = args[0]
        function = self.permanent_handlers.get(trigger_name)
        if not function:
            function = self.temporary_handlers.get(trigger_name)
        if function is not None:
            self.triggers.append(TriggerEvent(function, list(args[1:]), kwargs))
        else:
            log.error(f'Unknown trigger name "{trigger_name}" sent.')

    def display_name(self) -> str:
        handler_count = len(self.permanent_handlers) + len(self.temporary_handlers)
        trigger_count = len(self.triggers)
        return f'Timer[{handler_count} handlers, {trigger_count} triggers]'
