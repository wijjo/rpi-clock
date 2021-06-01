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
from typing import Optional

from rpiclock.events import EventProducersRegistry
from rpiclock.screen import Panel, Viewport
from rpiclock.utility import JSONDataSource, ImageDataSource, log

from .registry import PanelRegistry

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

STATIONS_SOURCE_NAME = 'weather-stations'
STATIONS_CACHE_TIMEOUT = 900    # refresh every 15 minutes
STATIONS_SUB_URL = '/gridpoints/{wfo}/{x},{y}/stations'
STATIONS_SCHEMA = {
    'observationStations': []
}

OBSERVATIONS_SOURCE_NAME = 'weather-observations'
OBSERVATIONS_CACHE_TIMEOUT = 900    # refresh every 15 minutes
OBSERVATIONS_SUB_URL = '/stations/{station}/observations/latest'
OBSERVATIONS_SCHEMA = {
    'properties': {
        'timestamp': str,
        'textDescription': str,
        'temperature': {
            'value': float,
            'unitCode': str,
        },
        'icon': str,
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
    station: str


@dataclass
class NOAAObservations:
    """Broken-out NOAA observation data."""

    timestamp: str
    description: str
    temperature: str
    icon: str

    def format(self, template: str) -> str:
        """
        strftime-like formatting

        %S: timestamp
        %T: temperature
        %D: description

        :param template: template string
        :return: formatted string
        """
        text = template
        if '%S' in text:
            text = text.replace('%S', self.timestamp)
        if '%T' in text:
            text = text.replace('%T', self.temperature)
        if '%D' in text:
            text = text.replace('%D', self.description)
        return text


class WeatherError(Exception):
    """Weather retrieval exception used internally."""
    pass


@PanelRegistry.register('weather')
class WeatherPanel(Panel):
    """NOAA weather panel."""

    # noinspection PyShadowingBuiltins
    def __init__(self,
                 latitude: float,
                 longitude: float,
                 format: str,
                 domain: str,
                 email: str,
                 metric: bool = False):
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
        :param format: strftime()-compatible format string
        :param domain: domain for user agent string as ID for NOAA API
        :param email: email for user agent string as ID for NOAA API
        :param metric: use metric (Celsius) units instead of Fahrenheit
        """
        self.latitude = latitude
        self.longitude = longitude
        self.weather_format = format
        self.metric = metric
        self.user_agent = f'({domain}, {email})'
        # Initialized in on_initialize().
        self.points_data_source: Optional[JSONDataSource] = None
        self.stations_data_source: Optional[JSONDataSource] = None
        self.observations_data_source: Optional[JSONDataSource] = None
        # No URL here, because download request provides entire URL.
        self.icon_data_source: Optional[ImageDataSource] = None
        self.text: Optional[str] = None
        self.icon_url: Optional[str] = None
        self.icon_path: Optional[str] = None
        self.ready = False
        self._noaa_params: Optional[NOAAParams] = None

    def do_update(self):
        """Called for initial and periodic updates."""
        self.icon_url = self.icon_path = None
        try:
            observations = self.get_latest_observations()
            if self.weather_format == ICON_FORMAT:
                if observations.icon:
                    self.text = None
                    self.icon_url = observations.icon
                    if self.icon_url:
                        self.icon_path = self.icon_data_source.download(self.icon_url)
            else:
                self.text = observations.format(self.weather_format)
        except WeatherError as exc:
            self.text = '--'
            log.error(f'Weather retrieval error: {str(exc)}')
        self.ready = True

    def on_initialize(self, event_producers_registry: EventProducersRegistry, viewport: Viewport):
        """
        Register handled events.

        :param event_producers_registry: event manager
        :param viewport: display viewport
        """
        self.points_data_source = JSONDataSource(POINTS_SOURCE_NAME,
                                                 BASE_URL,
                                                 POINTS_SUB_URL,
                                                 frequency=POINTS_CACHE_TIMEOUT,
                                                 schema=POINTS_SCHEMA,
                                                 user_agent=self.user_agent)
        self.stations_data_source = JSONDataSource(STATIONS_SOURCE_NAME,
                                                   BASE_URL,
                                                   STATIONS_SUB_URL,
                                                   frequency=STATIONS_CACHE_TIMEOUT,
                                                   user_agent=self.user_agent)
        self.observations_data_source = JSONDataSource(OBSERVATIONS_SOURCE_NAME,
                                                       BASE_URL,
                                                       OBSERVATIONS_SUB_URL,
                                                       frequency=OBSERVATIONS_CACHE_TIMEOUT,
                                                       user_agent=self.user_agent)
        # No URL here, because download request provides entire URL.
        self.icon_data_source = ImageDataSource('weather-icon',
                                                frequency=ICON_CACHE_TIMEOUT,
                                                extension=ICON_EXTENSION,
                                                user_agent=self.user_agent,
                                                dimensions=(viewport.inner_rect.width,
                                                            viewport.inner_rect.height))
        event_producers_registry.register('timer', self.do_update, POLL_FREQUENCY)
        self.do_update()

    @property
    def noaa_params(self) -> NOAAParams:
        """
        NOAA location parameters property.

        Retrieved and cached on first use.

        :return: NOAA parameters
        """
        if self._noaa_params is None:
            # Need grid points data in order to get local stations.
            points_data = self.points_data_source.download(latitude=self.latitude,
                                                           longitude=self.longitude)
            if points_data is None:
                raise WeatherError('NOAA geo data is unavailable')
            wfo = points_data['properties']['gridId']
            x = points_data['properties']['gridX']
            y = points_data['properties']['gridY']
            # Get local stations.
            stations_data = self.stations_data_source.download(wfo=wfo, x=x, y=y)
            # noinspection PyBroadException
            try:
                stations = [url.split('/')[-1] for url in stations_data['observationStations']]
            except Exception as exc:
                raise WeatherError(f'Bad or unexpected NOAA "observationStations" data: {exc}')
            if not stations:
                raise WeatherError('No weather stations found.')
            self._noaa_params = NOAAParams(wfo, x, y, stations[0])
        return self._noaa_params

    def get_latest_observations(self) -> NOAAObservations:
        """
        Download latest weather observations.

        :return: observations data
        """
        observations_data = self.observations_data_source.download(
            station=self.noaa_params.station)
        if observations_data is None:
            raise WeatherError('NOAA returned no observations data')
        if not isinstance(observations_data, dict):
            raise WeatherError('Badly format NOAA observations data')
        if 'properties' not in observations_data:
            raise WeatherError('NOAA observations data missing properties')
        properties = observations_data['properties']
        # Be careful to protect against unexpected data types, values, or structure.
        timestamp = properties.get('timestamp')
        if not timestamp or not isinstance(timestamp, str):
            timestamp = '--'
        description = properties.get('textDescription')
        if not description or not isinstance(description, str):
            description = '--'
        temperature = '--'
        temperature_data = properties.get('temperature')
        if not temperature_data or not isinstance(description, dict):
            temperature_value = temperature_data.get('value')
            if temperature_value and isinstance(temperature_value, (int, float)):
                if temperature_data.get('unitCode') == 'unit:degC':
                    if not self.metric:
                        temperature = f'{int(temperature_value * 1.8 + 32)}\u00b0'
                else:
                    if self.metric:
                        temperature = f'{int((temperature_value - 32) / 1.8)}\u00b0'
        icon = properties.get('icon')
        return NOAAObservations(timestamp, description, temperature, icon)

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
