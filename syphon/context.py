"""syphon.context.py

   Copyright (c) 2017-2018 Keithley Instruments, LLC.
   Licensed under MIT (https://github.com/ehall/syphon/blob/master/LICENSE)

"""
from sortedcontainers import SortedDict

class Context(object):
    """Runtime settings container."""
    def __init__(self):
        self._archive_dir = None
        self._cache = None
        self._data = None
        self._meta = None
        self._overwrite = False
        self._schema = None
        self._schema_file = '.schema.json'
        self._verbose = False

    @property
    def archive(self) -> str:
        """`str`: Absolute path to the archive directory."""
        return self._archive_dir

    @archive.setter
    def archive(self, value: str):
        self._archive_dir = value

    @property
    def cache(self) -> str:
        """`str`: Absolute filepath of the cache file."""
        return self._cache

    @cache.setter
    def cache(self, value: str):
        self._cache = value

    @property
    def data(self) -> str:
        """`str`: Absolute filepath or glob pattern of data file(s)."""
        return self._data

    @data.setter
    def data(self, value: str):
        self._data = value

    @property
    def meta(self) -> str:
        """`str`: Absolute filepath or glob pattern of metadata files(s)."""
        return self._meta

    @meta.setter
    def meta(self, value: str):
        self._meta = value

    @property
    def overwrite(self) -> bool:
        """`bool`: `True` to overwrite existing files, `False` otherwise."""
        return self._overwrite

    @overwrite.setter
    def overwrite(self, value: bool):
        self._overwrite = value

    @property
    def schema(self) -> SortedDict:
        """`SortedDict`: Ordered archive directory storage schema."""
        return self._schema

    @schema.setter
    def schema(self, value: SortedDict):
        self._schema = value

    @property
    def schema_file(self) -> str:
        """`str`: Name of the file containing the archive storage schema."""
        return self._schema_file

    @property
    def verbose(self) -> bool:
        """`bool`: `True` to output everything, `False` otherwise."""
        return self._verbose

    @verbose.setter
    def verbose(self, value: bool):
        self._verbose = value
