"""syphon.tests.unittestdata.py

   Copyright (c) 2017-2018 Keithley Instruments, LLC.
   Licensed under MIT (https://github.com/ehall/syphon/blob/master/LICENSE)

"""
from sortedcontainers import SortedDict, SortedList

class UnitTestData(object):
    def __init__(self):
        self._data_files = None
        self._meta_files = None
        self._filemap = None

    @property
    def data_files(self) -> SortedList:
        """`SortedList`: Ordered list of data files."""
        return self._data_files

    @data_files.setter
    def data_files(self, value: SortedList):
        self._data_files = value

    @property
    def meta_files(self) -> SortedList:
        """`SortedList`: Ordered list of metadata files."""
        return self._meta_files

    @meta_files.setter
    def meta_files(self, value: SortedList):
        self._meta_files = value

    @property
    def filemap(self) -> SortedDict:
        """`SortedDict`: Keys are data file strings. Each value is a
        list of associated metadata files."""
        return self._filemap

    @filemap.setter
    def filemap(self, value: SortedDict):
        self._filemap = value
