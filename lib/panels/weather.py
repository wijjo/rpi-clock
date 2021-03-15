# Copyright (C) 2021, Steven Cooper
#
# This file is part of rpi-clock.
#
# Rpi-clock is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Rpi-clock is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with rpi-clock.  If not, see <https://www.gnu.org/licenses/>.

"""Weather panel."""

from dataclasses import dataclass
from time import struct_time
from typing import Optional

from ..data_source import JSONDataSource, FileDataSource
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
FORECAST_CACHE_TIMEOUT = 900    # refresh every 15 minutes
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

ICON_SOURCE_NAME = 'weather-icon'
ICON_CACHE_TIMEOUT = 2592000    # refresh icon images every 30 days
ICON_EXTENSION = '.png'


# Special format string to display a conditions icon.
ICON_FORMAT = '%I'


@dataclass
class NOAAParams:
    """NOAA parameters for identifying weather source."""
    wfo: str
    x: int
    y: int


@dataclass
class NOAAForecast:
    """Broken-out NOAA forecast data."""

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
            text = text.replace('%T', f'{self.temperature}\u00b0')
        if '%W' in text:
            text = text.replace('%W', f'{self.wind_speed} {self.wind_direction}')
        if '%S' in text:
            text = text.replace('%S', self.short_forecast)
        if '%D' in text:
            text = text.replace('%S', self.detailed_forecast)
        return text


class WeatherError(Exception):
    """Weather retrieval exception used internally."""
    pass


class WeatherPanel(Panel):
    """NOAA weather panel."""

    def __init__(self,
                 latitude: float,
                 longitude: float,
                 weather_format: str,
                 domain: str,
                 email: str):
        """
        Weather panel constructor.

        Uses the NOAA web API for data. Note that the domain and email address
        are required for identification to the NOAA API so that they can
        associate and resolve usage issues.

        The weather_format string accepts a special "%I" value to retrieve and
        display the current conditions icon (56x56 pixels).

        Local caching should prevent excessive online API hammering.

        :param latitude: weather location latitude
        :param longitude: weather location longitude
        :param weather_format: strftime()-compatible format string
        :param domain: domain for user agent string as ID for NOAA API
        :param email: email for user agent string as ID for NOAA API
        """
        self.latitude = latitude
        self.longitude = longitude
        self.weather_format = weather_format
        user_agent = f'({domain}, {email})'
        self.points_data_source = JSONDataSource(POINTS_SOURCE_NAME,
                                                 BASE_URL,
                                                 POINTS_SUB_URL,
                                                 frequency=POINTS_CACHE_TIMEOUT,
                                                 schema=POINTS_SCHEMA,
                                                 user_agent=user_agent)
        self.forecast_data_source = JSONDataSource('weather-forecast',
                                                   BASE_URL,
                                                   FORECAST_SUB_URL,
                                                   frequency=FORECAST_CACHE_TIMEOUT,
                                                   user_agent=user_agent)
        # No URL here, because download request provides entire URL.
        self.icon_data_source = FileDataSource('weather-icon',
                                               frequency=ICON_CACHE_TIMEOUT,
                                               extension=ICON_EXTENSION,
                                               user_agent=user_agent)
        self.text: Optional[str] = None
        self.icon_url: Optional[str] = None
        self.icon_path: Optional[str] = None
        self.ready = False
        self._noaa_params: Optional[NOAAParams] = None
        self.do_update()

    def do_update(self):
        """Called for initial and periodic updates."""
        self.icon_url = self.icon_path = None
        try:
            forecast = self.get_forecast(1)
            if self.weather_format == ICON_FORMAT:
                if forecast.icon:
                    self.text = None
                    self.icon_url = forecast.icon
                    if self.icon_url:
                        self.icon_path = self.icon_data_source.download(self.icon_url)
            else:
                self.text = forecast.format(self.weather_format)
        except WeatherError as exc:
            self.text = f'*{exc}*'
        self.ready = True

    def on_initialize_events(self, event_manager: EventManager):
        """
        Register handled events.

        :param event_manager: event manager
        """
        event_manager.register('timer', self.do_update, POLL_FREQUENCY)

    @property
    def noaa_params(self) -> NOAAParams:
        """
        NOAA location parameters property.

        Retrieved and cached on first use.

        :return: NOAA parameters
        """
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
        """
        Download weather forecast by index.

        Received data is a time-sequenced series with #1 being current.

        :param forecast_idx:
        :return: forecast data
        """
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
        """
        Display the requested data in a viewport.

        :param viewport: viewport for display
        """
        if self.icon_url:
            if self.icon_path:
                viewport.image(self.icon_path)
            else:
                viewport.text('(no icon)')
        else:
            viewport.text(self.text)
        self.ready = False

    def on_check(self) -> bool:
        """
        Check if data is ready for display.

        :return: True if data is ready
        """
        return self.ready
