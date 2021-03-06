from dataclasses import dataclass
from time import struct_time
from typing import Optional

from ..data_source import JSONDataSource
from ..event_manager import EventManager
from ..panel import Panel
from ..viewport import Viewport

# It's okay to poll more often, because the data source is cached.
POLL_FREQUENCY = 60
BASE_URL = 'https://api.weather.gov'

# Points are never automatically refreshed.
POINTS_SOURCE_NAME = 'weather-points'
POINTS_CACHE_TIMEOUT = 0        # 0 == use forever
POINTS_SUB_URL = '/points/{latitude:.4f},{longitude:.4f}'
POINTS_SCHEMA = {
    'properties': {
        'gridId': str,
        'gridX': int,
        'gridY': int
    }
}

FORECAST_SOURCE_NAME = 'weather-forecast'
FORECAST_CACHE_TIMEOUT = 900    # refresh every 5 minutes
# From points schema: wfo==gridId, x=gridX, and y=gridY.
FORECAST_SUB_URL = '/gridpoints/{wfo}/{x},{y}/forecast/hourly'
FORECAST_SCHEMA = {
    'properties': {
        'updateTime': str,
        'periods': [
            {
                'number': int,
                'name': str,
                'startTime': str,
                'endTime': str,
                'isDaytime': bool,
                'temperature': int,
                'temperatureUnit': str,
                'temperatureTrend': Optional[str],
                'windSpeed': str,
                'windDirection': str,
                'icon': str,
                'shortForecast': str,
                'detailedForecast': str
            }
        ]
    }
}


@dataclass
class NOAAParams:
    wfo: str
    x: int
    y: int


@dataclass
class NOAAForecast:
    start_time: struct_time
    end_time: struct_time
    is_daytime: bool
    temperature: int
    temperature_unit: str
    trend: str
    wind_speed: str
    wind_direction: str
    icon: str
    short_forecast: str
    detailed_forecast: str

    def format(self, template: str) -> str:
        """
        strftime-like formatting

        %T: temperature
        %W: wind
        %S: short forecast
        %D: detailed forecast

        :param template: template string
        :return: formatted string
        """
        text = template
        if '%T' in text:
            text = text.replace('%T', f'{self.temperature}\u00b0{self.temperature_unit}')
        if '%W' in text:
            text = text.replace('%W', f'{self.wind_speed} {self.wind_direction}')
        if '%S' in text:
            text = text.replace('%S', self.short_forecast)
        if '%D' in text:
            text = text.replace('%S', self.detailed_forecast)
        return text


class WeatherError(Exception):
    pass


class WeatherPanel(Panel):

    def __init__(self, latitude: float, longitude: float, weather_format: str):
        self.ready = True
        self.latitude = latitude
        self.longitude = longitude
        self.weather_format = weather_format
        self.points_data_source = JSONDataSource(POINTS_SOURCE_NAME,
                                                 BASE_URL,
                                                 POINTS_SUB_URL,
                                                 frequency=POINTS_CACHE_TIMEOUT,
                                                 schema=POINTS_SCHEMA)
        self.forecast_data_source = JSONDataSource('weather-forecast',
                                                   BASE_URL,
                                                   FORECAST_SUB_URL,
                                                   frequency=FORECAST_CACHE_TIMEOUT)
        self.text = 'Waiting for weather data...'
        self._noaa_params: Optional[NOAAParams] = None

    def on_initialize(self, event_manager: EventManager):
        def _timeout():
            self.ready = True
        event_manager.register('timer', _timeout, POLL_FREQUENCY)

    @property
    def noaa_params(self) -> NOAAParams:
        if self._noaa_params is None:
            points_data = self.points_data_source.download(latitude=self.latitude,
                                                           longitude=self.longitude)
            if points_data is None:
                raise WeatherError('NOAA geo data is unavailable')
            self._noaa_params = NOAAParams(points_data['properties']['gridId'],
                                           points_data['properties']['gridX'],
                                           points_data['properties']['gridY'])
        return self._noaa_params

    def get_forecast(self, forecast_idx: int) -> NOAAForecast:
        forecast_data = self.forecast_data_source.download(wfo=self.noaa_params.wfo,
                                                           x=self.noaa_params.x,
                                                           y=self.noaa_params.y)
        if forecast_data is None:
            raise WeatherError('NOAA forecast is unavailable')
        for period_data in forecast_data['properties']['periods']:
            if period_data['number'] == forecast_idx:
                return NOAAForecast(period_data['startTime'],
                                    period_data['endTime'],
                                    period_data['isDaytime'],
                                    period_data['temperature'],
                                    period_data['temperatureUnit'],
                                    period_data['temperatureTrend'],
                                    period_data['windSpeed'],
                                    period_data['windDirection'],
                                    period_data['icon'],
                                    period_data['shortForecast'],
                                    period_data['detailedForecast'])
        raise WeatherError(f'NOAA forecast #{forecast_idx} not found')

    def on_display(self, viewport: Viewport):
        try:
            forecast = self.get_forecast(1)
            self.text = forecast.format(self.weather_format)
        except WeatherError as exc:
            self.text = f'*{exc}*'
        viewport.text(self.text)
        self.ready = False

    def on_check(self) -> bool:
        return self.ready
