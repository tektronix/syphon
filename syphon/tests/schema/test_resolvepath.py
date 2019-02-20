"""syphon.tests.schema.test_resolvepath.py

   Copyright Keithley Instruments, LLC.
   Licensed under MIT (https://github.com/tektronix/syphon/blob/master/LICENSE)

"""
from os.path import join

import pytest
from numpy import nan
from pandas.util.testing import makeCustomIndex
from sortedcontainers import SortedDict
from syphon.schema import resolve_path

from .. import make_dataframe, make_dataframe_value


class TestResolvePath(object):
    archive = '.\\'
    headers = makeCustomIndex(7, 1, prefix='C')

    multi_schema = SortedDict({
        '0': headers[1],
        '1': headers[3]
    })
    multi_schema2 = SortedDict({
        '0': headers[0],
        '1': headers[2],
        '2': headers[3]
    })
    multi_schema3 = SortedDict({
        '0': headers[1],
        '1': headers[6]
    })

    single_schema = SortedDict({
        '0': headers[0],
    })
    single_schema2 = SortedDict({
        '0': headers[4]
    })

    @staticmethod
    def data_gen_invalid(row: int, col: int):
        valmap_invalid = [
            ['val', 'val', 'xxx', 'val'],
            ['val',   nan, 'val', 'val'],
            ['val',   nan, 'val',   nan],
            [  nan,   nan, 'val', 'xxx'],   # noqa: E201
            ['xxx',   nan, 'val',   nan]
        ]

        if row < len(valmap_invalid):
            if col < len(valmap_invalid[row]):
                return valmap_invalid[row][col]
        return make_dataframe_value(row, col)

    @staticmethod
    def data_gen(row: int, col: int):
        valmap = [
            ['val', 'val', 'val', 'val'],
            ['val',   nan, 'val', 'val'],
            ['val',   nan, 'val',   nan],
            [  nan,   nan, 'val',   nan],   # noqa: E201
            [  nan,   nan, 'val',   nan]    # noqa: E201
        ]

        if row < len(valmap):
            if col < len(valmap[row]):
                return valmap[row][col]
        return make_dataframe_value(row, col)

    @staticmethod
    def data_gen_normalizable(row: int, col: int):
        valmap = [
            ['Value 1.', 'Value 1.', 'Value 1.', 'Value 1.'],
            ['Value 1.',        nan, 'Value 1.', 'Value 1.'],
            ['Value 1.',        nan, 'Value 1.',        nan],
            [       nan,        nan, 'Value 1.',        nan],   # noqa: E201
            [       nan,        nan, 'Value 1.',        nan]    # noqa: E201
        ]

        if row < len(valmap):
            if col < len(valmap[row]):
                return valmap[row][col]
        return make_dataframe_value(row, col)

    @pytest.mark.parametrize('schema, expected', [
        (single_schema, join(archive, 'val')),
        (multi_schema, join(archive, 'val', 'val')),
        (multi_schema2, join(archive, 'val', 'val', 'val')),
    ])
    def test_resolve_path(self, schema, expected):
        data = make_dataframe(5, 4, data_gen_f=TestResolvePath.data_gen)

        actual = resolve_path(self.archive, schema, data)

        assert actual == expected

    @pytest.mark.parametrize('schema, expected', [
        (single_schema, join(archive, 'value_1')),
        (multi_schema, join(archive, 'value_1', 'value_1')),
        (multi_schema2, join(archive, 'value_1', 'value_1', 'value_1'))
    ])
    def test_resolve_path_normalized(self, schema, expected):
        data = make_dataframe(
            5, 4, data_gen_f=TestResolvePath.data_gen_normalizable)

        actual = resolve_path(self.archive, schema, data)

        assert actual == expected

    @pytest.mark.parametrize('schema', [
        single_schema2,
        multi_schema3,
    ])
    def test_resolve_path_indexerror(self, schema):
        data = make_dataframe(5, 4, data_gen_f=TestResolvePath.data_gen)

        with pytest.raises(IndexError):
            resolve_path(self.archive, schema, data)

    @pytest.mark.parametrize('schema', [
        single_schema,
        multi_schema,
        multi_schema2,
    ])
    def test_resolve_path_valueerror(self, schema):
        data = make_dataframe(
            5, 4, data_gen_f=TestResolvePath.data_gen_invalid)

        with pytest.raises(ValueError):
            resolve_path(self.archive, schema, data)
