"""syphon.tests.schema.test_resolvepath.py

   Copyright Keithley Instruments, LLC.
   Licensed under MIT (https://github.com/tektronix/syphon/blob/master/LICENSE)

"""
from os.path import join
from typing import List, Union

import pytest
from numpy import nan
from pandas import DataFrame, Index
from pandas.util.testing import makeCustomIndex
from sortedcontainers import SortedDict

from syphon.schema import resolve_path

from .. import make_dataframe, make_dataframe_value


class TestResolvePath(object):
    archive = ".\\"
    headers: Index = makeCustomIndex(7, 1, prefix="C")

    multi_schema = SortedDict({"0": headers[1], "1": headers[3]})
    multi_schema2 = SortedDict({"0": headers[0], "1": headers[2], "2": headers[3]})
    multi_schema3 = SortedDict({"0": headers[1], "1": headers[6]})

    single_schema = SortedDict({"0": headers[0]})
    single_schema2 = SortedDict({"0": headers[4]})

    @staticmethod
    def data_gen_invalid(row: int, col: int) -> Union[float, str]:
        # Invalid data has:
        # 1) multiple data values per column (excluding NaNs).
        # 2) NaNs between data values.
        # fmt: off
        valmap_invalid: List[List[Union[float, str]]] = [
            ["val", "val", "xxx", "val"],
            ["val",   nan, "val", "val"],  # noqa: E241
            ["val",   nan, "val",   nan],  # noqa: E241
            [  nan,   nan, "val", "xxx"],  # noqa: E201, E241
            ["xxx",   nan, "val",   nan],  # noqa: E241
        ]
        # fmt: on

        if row < len(valmap_invalid):
            if col < len(valmap_invalid[row]):
                return valmap_invalid[row][col]
        # Use pandas' value generation function if the given (row, column) falls
        # outside our pre-defined invalid value map.
        return make_dataframe_value(row, col)

    @staticmethod
    def data_gen(row: int, col: int) -> Union[float, str]:
        # Valid data has:
        # 1) the same data value for each column.
        # 2) contiguous data (no NaNs between data values).
        # fmt: off
        valmap: List[List[Union[float, str]]] = [
            ["val", "val", "val", "val"],
            ["val",   nan, "val", "val"],  # noqa: E241
            ["val",   nan, "val",   nan],  # noqa: E241
            [  nan,   nan, "val",   nan],  # noqa: E201, E241
            [  nan,   nan, "val",   nan],  # noqa: E201, E241
        ]
        # fmt: on

        if row < len(valmap):
            if col < len(valmap[row]):
                return valmap[row][col]
        # Fall back on pandas' value generator.
        return make_dataframe_value(row, col)

    @staticmethod
    def data_gen_normalizable(row: int, col: int) -> Union[float, str]:
        # A valid data map containing data values that will be normalized by
        # `syphon.schema.resolvepath._normalize`.
        # fmt: off
        valmap: List[List[Union[float, str]]] = [
            ["Value 1.", "Value 1.", "Value 1.", "Value 1."],
            ["Value 1.",        nan, "Value 1.", "Value 1."],  # noqa: E241
            ["Value 1.",        nan, "Value 1.",        nan],  # noqa: E241
            [       nan,        nan, "Value 1.",        nan],  # noqa: E201, E241
            [       nan,        nan, "Value 1.",        nan],  # noqa: E201, E241
        ]
        # fmt: on

        if row < len(valmap):
            if col < len(valmap[row]):
                return valmap[row][col]
        # Fall back on pandas' value generator.
        return make_dataframe_value(row, col)

    @pytest.mark.parametrize(
        "schema, expected",
        [
            (single_schema, join(archive, "val")),
            (multi_schema, join(archive, "val", "val")),
            (multi_schema2, join(archive, "val", "val", "val")),
        ],
    )
    def test_resolve_path(self, schema: SortedDict, expected: str):
        data: DataFrame = make_dataframe(5, 4, data_gen_f=TestResolvePath.data_gen)
        actual: str = resolve_path(self.archive, schema, data)

        assert actual == expected

    @pytest.mark.parametrize(
        "schema, expected",
        [
            (single_schema, join(archive, "value_1")),
            (multi_schema, join(archive, "value_1", "value_1")),
            (multi_schema2, join(archive, "value_1", "value_1", "value_1")),
        ],
    )
    def test_resolve_path_normalized(self, schema: SortedDict, expected: str):
        data: DataFrame = make_dataframe(
            5, 4, data_gen_f=TestResolvePath.data_gen_normalizable
        )
        actual: str = resolve_path(self.archive, schema, data)

        assert actual == expected

    @pytest.mark.parametrize("schema", [single_schema2, multi_schema3])
    def test_resolve_path_indexerror(self, schema: SortedDict):
        data: DataFrame = make_dataframe(5, 4, data_gen_f=TestResolvePath.data_gen)

        with pytest.raises(IndexError):
            resolve_path(self.archive, schema, data)

    @pytest.mark.parametrize("schema", [single_schema, multi_schema, multi_schema2])
    def test_resolve_path_valueerror(self, schema: SortedDict):
        data: DataFrame = make_dataframe(
            5, 4, data_gen_f=TestResolvePath.data_gen_invalid
        )

        with pytest.raises(ValueError):
            resolve_path(self.archive, schema, data)
