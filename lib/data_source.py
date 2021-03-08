import json
import os
from time import time
from urllib.parse import quote
from urllib.request import urlopen, Request
from typing import Dict, List, Optional, Union, Any

from . import log
from .typing import Interval

Schema = Union[Dict[str, Union[type, 'Schema']], List['Schema']]


class JSONDataSource:
    """ReST API JSON data source with optional caching to minimize API usage."""

    cache_folder = '/tmp/rpi-clock/data-cache'

    def __init__(self,
                 name: str,
                 *url_parts: str,
                 user_agent: str = None,
                 frequency: Interval = None,
                 schema: Schema = None):
        """
        Construct JSON data source.

        Cache frequency zero is only downloaded once and never replaced.

        The optional properties parameter serves as a "poor man's" JSON schema
        for quickly checking that all required parameters are present. It is
        structured as a possibly-nested collection of lists and dictionaries
        that map to the structure of expected properties. Lists have only one
        element in the schema, but the received data may have any quantity.

        Methods of this class log informative errors when problems occur.

        :param name: data source name
        :param url: download URL, possibly including {<name>} template fields
        :param user_agent: optional user agent string
        :param frequency: update/cache frequency in seconds (default: not cached)
        :param schema: simple schema used to check for missing properties
        """
        self.name = name
        self.user_agent = user_agent or 'Mozilla'
        self.url = ''.join(url_parts)
        self.frequency = frequency
        self.schema = schema

    @classmethod
    def get_cache_path(cls, url: str) -> str:
        """
        Determine cached data file path based on URL.

        :param url: URL that provides the data online
        :return: path constructed to include properly-escaped URL string
        """
        return os.path.join(cls.cache_folder, quote(url))

    @classmethod
    def get_cache_data(cls,
                       url: str,
                       frequency: Optional[Interval],
                       ) -> Optional[Any]:
        """
        Cached data reading and expiration handling.

        Deletes cache files when they expire.

        Cache frequency zero is only downloaded once and never replaced.

        :param url: URL for looking up cached data
        :param frequency: update/cache frequency in seconds (default: not cached)
        :return: data if cache is available and has not expired
        """
        if frequency is None:
            return None
        path = cls.get_cache_path(url)
        if not os.path.isfile(path):
            return None
        if frequency > 0:
            mtime = os.path.getmtime(path)
            if time() - mtime > frequency:
                os.remove(path)
                return None
        # noinspection PyBroadException
        try:
            with open(path, encoding='utf-8') as cache_file:
                return json.load(cache_file)
        except Exception as exc:
            log.error(f'Failed to read or encode cached data for "{url}": {exc}')
            if os.path.isfile(path):
                os.remove(path)
            return None

    @classmethod
    def put_cache_data(cls, url: str, data: Any):
        """
        Write cache data.

        :param url: URL to convert to a file path
        :param data: data to save to cache
        """
        path = cls.get_cache_path(url)
        # noinspection PyBroadException
        try:
            folder = os.path.dirname(path)
            if not os.path.isdir(folder):
                os.makedirs(folder)
            with open(path, 'w', encoding='utf-8') as cache_file:
                json.dump(data, cache_file)
        except Exception as exc:
            log.error(f'Failed to write or encode cached data for "{url}": {exc}')
            if os.path.isfile(path):
                os.remove(path)

    @classmethod
    def _check_data(cls, data: object, schema: Optional[Schema]) -> bool:

        # Check list schema?
        if schema and isinstance(schema, list):
            if not isinstance(data, list):
                return False
            if len(schema) != 1:
                log.error('More than one item in data source schema list.')
                return False
            for sub_data in data:
                if not cls._check_data(sub_data, schema[0]):
                    return False
            return True

        # Check dictionary schema?
        if schema and isinstance(schema, dict):
            for name, sub_schema in schema.items():
                if name not in data:
                    return False
                # noinspection PyUnresolvedReferences
                if not cls._check_data(data[name], sub_schema):
                    return False
            return True

        # Don't check anything else.
        return True

    def download(self, *args, **kwargs) -> Optional[Any]:
        """
        Download data from possibly-parameterized URL.

        If a schema was provided to the constructor, the caller can assume any
        non-None return will have all expected properties present.

        :param args: positional parameters to resolve URL template fields
        :param kwargs: keyword parameters to resolve URL template fields
        :return: data if successful or None otherwise
        """
        url = self.url.format(*args, **kwargs)
        data = self.get_cache_data(url, self.frequency)
        if data is not None:
            log.info(f'Load cache: {url}')
            return data
        log.info(f'Download: {url}')
        # noinspection PyBroadException
        try:
            request = Request(url, data=None, headers={'User-Agent': self.user_agent})
            response = urlopen(request)
            raw_data = response.read()
            data = json.loads(raw_data)
            if not self._check_data(data, self.schema):
                log.error(f'Data from "{url}" is missing expected properties.')
                return None
            self.put_cache_data(url, data)
        except Exception as exc:
            log.error(f'Failed to download or decode data from "{url}": {exc}')
            return None
        return data
