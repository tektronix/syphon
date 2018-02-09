"""syphon.tests.schema.test_resolvepath.py

   Copyright (c) 2017-2018 Keithley Instruments, LLC.
   Licensed under MIT (https://github.com/ehall/syphon/blob/master/LICENSE)

"""
import pytest
from pandas import DataFrame, read_csv
from pandas.compat import StringIO
from sortedcontainers import SortedDict

from syphon.schema import resolve_path

from .. import make_dataframe, make_dataframe_value

class TestResolvePath(object):
    @staticmethod
    def invalid_value_map(row: int, col: int):
        from numpy import nan

        valmap = [
            [None, None,  None, None],
            [None,  nan,  None, None],
            [None,  nan,  None,  nan],
            [ nan,  nan, 'val',  nan],
            [ nan,  nan, 'val',  nan]
        ]

        if row < len(valmap):
            if col < len(valmap[row]):
                if valmap[row][col] is not None:
                    if valmap[row][col] is nan:
                        return nan
                    else:
                        return valmap[row][col]
        return make_dataframe_value(row, col)

    @staticmethod
    def valid_value_map(row: int, col: int):
        from numpy import nan

        valmap = [
            [None, None, None, None],
            [None,  nan, None, None],
            [None,  nan, None,  nan],
            [ nan,  nan, None,  nan],
            [ nan,  nan, None,  nan]
        ]

        if row < len(valmap):
            if col < len(valmap[row]):
                if valmap[row][col] is not None:
                    return nan
        return make_dataframe_value(row, col)
