from ..event_manager import EventManager
from ..panel import Panel
from ..viewport import Viewport


class WeatherPanel(Panel):

    def __init__(self, latitude: float, longitude: float):
        self.ready = True
        self.latitude_longitude = f'{latitude:.4f},{longitude:.4f}'
        self.text = f'(weather for {self.latitude_longitude})'

    def on_initialize(self, event_manager: EventManager):
        # Refresh weather every 15 minutes.
        event_manager.register('timer', self.timeout, 900)

    def on_display(self, viewport: Viewport):
        viewport.text(self.text)
        self.ready = False

    def on_check(self) -> bool:
        return self.ready

    def timeout(self):
        self.text = f'rainy, snowy, and all that'
        self.ready = True
