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

"""Internet data source support classes."""

import json
import os
import re
from dataclasses import dataclass
from time import time
from urllib.parse import quote
from urllib.request import urlopen, Request
from typing import Dict, List, Optional, Union, Any

from rpiclock import log
from rpiclock.typing import Interval

Schema = Union[Dict[str, Union[type, 'Schema']], List['Schema']]

URL_STRIP_REGEX = re.compile(r'^[^/:]+://')


@dataclass
class DownloadResult:
    """Returned by DataSource download handler with in-memory and cached data."""
    data: Any
    """In-memory data."""
    cache: Optional[Union[str, bytes]]
    """Cached data."""


class DataSource:
    """Generic data source with optional caching to minimize API usage."""

    cache_folder = '/tmp/rpi-clock-cache'

    def __init__(self,
                 name: str,
                 *url_parts: str,
                 user_agent: str = None,
                 frequency: Interval = None):
        """
        Construct generic data source.

        Cache frequency zero is only downloaded once and never replaced.

        :param name: data source name
        :param url: download URL, possibly including {<name>} template fields
        :param user_agent: optional user agent string
        :param frequency: update/cache frequency in seconds (default: not cached)
        """
        self.name = name
        self.user_agent = user_agent or 'Mozilla'
        if url_parts:
            self.url: Optional[str] = '/'.join([
                url_part[1:] if url_part.startswith('/') else url_part
                for url_part in url_parts
            ])
        else:
            self.url: Optional[str] = None
        self.frequency = frequency

    def get_cache_path(self, url: str) -> str:
        """
        Determine cached data file path based on URL.

        :param url: URL that provides the data online
        :return: path constructed to include properly-escaped URL string
        """
        # Strip off leading https://, etc.. Escape inappropriate characters.
        # Make sure the cache folder has only a single level of file folders.
        strip_match = URL_STRIP_REGEX.match(url)
        if strip_match is not None:
            url = url[strip_match.end():]
        base_path = os.path.join(self.cache_folder, quote(url).replace('/', '_'))
        return self.on_generate_cache_path(url, base_path)

    def load_cache(self, path: str, frequency: Interval) -> Optional[Any]:
        """
        Cached data reading and expiration handling.

        Deletes cache files when they expire.

        Cache frequency zero is only downloaded once and never replaced.

        :param path: cache file path
        :param frequency: update/cache frequency in seconds (default: not cached)
        :return: data if cache is available and has not expired
        """
        if frequency > 0:
            mtime = os.path.getmtime(path)
            if time() - mtime > frequency:
                os.remove(path)
                return None
        try:
            return self.on_load_cache_file(path)
        except Exception as exc:
            log.error(f'Data source "{self.name}" failed to load data from cache'
                      f' file "{path}": {exc}')
            if os.path.isfile(path):
                os.remove(path)
            return None

    def save_cache(self, path: str, data: Union[str, bytes]) -> bool:
        """
        Write cache data.

        Cache folders and files have open permissions so that they are easy for
        any user to delete.

        :param path: cache file path
        :param data: downloaded data to save to cache
        :return: True if successful
        """
        try:
            folder = os.path.dirname(path)
            # TODO: The hard-coded "chown" allows the "pi" user to delete the cache.
            if not os.path.isdir(folder):
                os.system(f'mkdir {folder}')
                os.system(f'chown pi:pi {folder}')
            self.on_save_cache_file(path, data)
            os.system(f'chown pi:pi {path}')
            return True
        except Exception as exc:
            log.error(f'Data source "{self.name}" failed to write data to cache'
                      f' file "{path}": {exc}')
            if os.path.isfile(path):
                os.remove(path)
            return False

    def download(self, *args, **kwargs) -> Optional[Any]:
        """
        Download data from possibly-parameterized URL.

        The first positional argument must be a URL if no base URL was given to
        the constructor.

        :param args: positional parameters to resolve URL template fields
        :param kwargs: keyword parameters to resolve URL template fields
        :return: data if successful or None otherwise
        """
        if self.url is None:
            if not args:
                log.error(f'Data source "{self.name}" download call requires'
                          f' a URL argument.')
                return None
            url_template = args[0]
            args = args[1:]
        else:
            url_template = self.url
        url = url_template.format(*args, **kwargs)
        cache_path = self.get_cache_path(url)
        if self.frequency is not None and os.path.isfile(cache_path):
            cache_data = self.load_cache(cache_path, self.frequency)
            if cache_data is not None:
                log.info(f'Load cache: {cache_path}')
                return cache_data
        # noinspection PyBroadException
        try:
            log.info(f'Download: {url}')
            request = Request(url)
            # The National Weather Service wants the User-Agent header. For some
            # unknown reason, the Accept header is needed in order to receive
            # data for the correct timezone, or to properly handle local time.
            request.add_header('User-Agent', self.user_agent)
            request.add_header('Accept', '*/*')
            response = urlopen(request)
            raw_data = response.read()
            download = self.on_process_download(raw_data, cache_path)
            if download.cache is not None:
                if not self.save_cache(cache_path, download.cache):
                    return None
            return download.data
        except Exception as exc:
            log.error(f'Data source "{self.name}" failed to download data'
                      f' from "{url}": {exc}')
            return None

    # === Required overrides.

    def on_process_download(self,
                            data: Union[str, bytes],
                            cache_path: str,
                            ) -> DownloadResult:
        """
        Required override to check and massage downloaded data.

        :param data: raw data
        :param cache_path: future cache file path
        :return: returned bundle of massaged data and cache
        :raise: I/O or other exception
        """
        raise NotImplementedError

    def on_generate_cache_path(self, url: str, base_path: str) -> str:
        """
        Required override to generate a cache path based on a URL.

        :param url: source URL
        :param base_path: base cache path
        :return: full cache file path
        """
        raise NotImplementedError

    def on_load_cache_file(self, path: str) -> Any:
        """
        Required override to load, check, and massage cached data.

        Caller handles exceptions.

        :param path: cache file path
        :return: possibly-altered data or None if it fails to validate
        :raise: I/O or other exception
        """
        raise NotImplementedError

    def on_save_cache_file(self, path: str, data: Union[str, bytes]):
        """
        Required override to save cache data.

        Caller handles exceptions.

        :param path: cache file path
        :param data: data to save
        :raise: I/O or other exception
        """
        raise NotImplementedError


class JSONDataSource(DataSource):
    """ReST API JSON data source with optional caching to minimize API usage."""

    def __init__(self,
                 name: str,
                 *url_parts: str,
                 user_agent: str = None,
                 frequency: Interval = None,
                 schema: Schema = None):
        """
        Construct JSON data source.

        Cache frequency zero is only downloaded once and never replaced.

        The optional schema serves as a "poor man's" JSON schema for quickly
        checking that all required parameters are present. It is a
        potentially-nested collection of lists and dictionaries that map to the
        structure of expected properties. Lists have only one element in the
        schema, but the received data may have any quantity.

        :param name: data source name
        :param url: download URL, possibly including {<name>} template fields
        :param user_agent: optional user agent string
        :param frequency: update/cache frequency in seconds (default: not cached)
        :param schema: simple schema used to check for missing properties
        """
        super().__init__(name, *url_parts, user_agent=user_agent, frequency=frequency)
        self.schema = schema

    # === Required overrides.

    def on_process_download(self,
                            data: Union[str, bytes],
                            cache_path: str,
                            ) -> DownloadResult:
        """
        Required override to check and massage downloaded data.

        :param data: raw data
        :param cache_path: future cache file path
        :return: returned bundle of massaged data and cache
        :raise: I/O, JSON, or schema validation exception
        """
        json_data = json.loads(data)
        self._check_schema(json_data, self.schema)
        json_cache = json.dumps(json_data, indent=2)
        return DownloadResult(json_data, json_cache)

    def on_generate_cache_path(self, url: str, base_path: str) -> str:
        """
        Required override to generate a cache path based on a URL.

        :param url: source URL
        :param base_path: base cache path
        :return: full cache file path
        """
        return f'{base_path}.json'

    def on_load_cache_file(self, path: str) -> Any:
        """
        Required override to load, check, and massage cached data.

        Caller handles exceptions.

        :param path: cache file path
        :return: possibly-altered data or None if it fails to validate
        :raise: I/O or JSON exception
        """
        with open(path, encoding='utf-8') as cache_file:
            return json.load(cache_file)

    def on_save_cache_file(self, path: str, data: Union[str, bytes]):
        """
        Required override to save cache data.

        Caller handles exceptions.

        :param path: cache file path
        :param data: data to save
        :raise: I/O or other exception
        """
        with open(path, 'w', encoding='utf-8') as cache_file:
            cache_file.write(data)

    # === Private methods.

    @classmethod
    def _check_schema(cls, data: Any, sub_schema: Optional[Schema]):
        # Check list schema?
        if isinstance(sub_schema, list):
            if not isinstance(data, list):
                raise ValueError(f'JSON data is not expected list type: {data}')
            if len(sub_schema) != 1:
                raise TypeError('More than one item in JSON data source schema list.')
            for item_data in data:
                cls._check_schema(item_data, sub_schema[0])
            return
        # Check dictionary schema?
        if isinstance(sub_schema, dict):
            for name, sub_schema in sub_schema.items():
                if name not in data:
                    raise ValueError(f'JSON data does not have expected'
                                     f' "{name}" element: {data}')
                # noinspection PyUnresolvedReferences
                cls._check_schema(data[name], sub_schema)


class FileDataSource(DataSource):
    """Data source that downloads files."""

    def __init__(self,
                 name: str,
                 *url_parts: str,
                 user_agent: str = None,
                 frequency: Interval = None,
                 extension: str = None,
                 encoding: str = None):
        """
        Construct file data source.

        Cache frequency zero is only downloaded once and never replaced.

        TODO: Multiple file type/extension/encoding support?

        :param name: data source name
        :param url: download URL, possibly including {<name>} template fields
        :param user_agent: optional user agent string
        :param frequency: update/cache frequency in seconds (default: not cached)
        :param extension: optional file extension to append
        :param encoding: optional text file encoding
        """
        super().__init__(name, *url_parts, user_agent=user_agent, frequency=frequency)
        self.extension = extension or ''
        self.encoding = encoding

    def on_process_download(self,
                            data: Union[str, bytes],
                            cache_path: str,
                            ) -> DownloadResult:
        """
        Required override to check and massage downloaded data.

        :param data: raw data
        :param cache_path: future cache file path
        :return: returned bundle of massaged data and cache
        :raise: I/O or other exception
        """
        return DownloadResult(cache_path, data)

    def on_generate_cache_path(self, url: str, base_path: str) -> str:
        """
        Required override to generate a cache path based on a URL.

        :param url: source URL
        :param base_path: base cache path
        :return: full cache file path
        """
        return f'{base_path}{self.extension}'

    def on_load_cache_file(self, path: str) -> Any:
        """
        Required override to load, check, and massage cached data.

        :param path: cache file path
        :return: cache file path as data
        :raise: I/O exception (won't happen here)
        """
        return path

    def on_save_cache_file(self, path: str, data: Union[str, bytes]):
        """
        Required override to save cache data.

        Caller handles exceptions.

        :param path: cache file path
        :param data: data to save
        :raise: I/O or other exception
        """
        mode = 'wb' if self.encoding is None else 'w'
        with open(path, mode, encoding=self.encoding) as cache_file:
            return cache_file.write(data)
