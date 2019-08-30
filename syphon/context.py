"""syphon.context.py

   Copyright Keithley Instruments, LLC.
   Licensed under MIT (https://github.com/tektronix/syphon/blob/master/LICENSE)

"""
from typing import Optional

from sortedcontainers import SortedDict


class Context:
    """Runtime settings container."""

    def __init__(self):
        self._archive_dir: Optional[str] = None
        self._cache: Optional[str] = None
        self._data: Optional[str] = None
        self._meta: Optional[str] = None
        self._overwrite: bool = False
        self._schema: SortedDict = SortedDict()
        self._schema_file: str = ".schema.json"
        self._verbose: bool = False

    @property
    def archive(self) -> Optional[str]:
        """`str`: Absolute path to the archive directory."""
        return self._archive_dir

    @archive.setter
    def archive(self, value: str):
        self._archive_dir = value

    @property
    def cache(self) -> Optional[str]:
        """`str`: Absolute filepath of the cache file."""
        return self._cache

    @cache.setter
    def cache(self, value: str):
        self._cache = value

    @property
    def data(self) -> Optional[str]:
        """`str`: Absolute filepath or glob pattern of data file(s)."""
        return self._data

    @data.setter
    def data(self, value: str):
        self._data = value

    @property
    def meta(self) -> Optional[str]:
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
