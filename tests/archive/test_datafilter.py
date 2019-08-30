"""syphon.tests.archive.test_datafilter.py

   Copyright Keithley Instruments, LLC.
   Licensed under MIT (https://github.com/tektronix/syphon/blob/master/LICENSE)

"""
from typing import Dict, List, Optional, Tuple

import pytest
from pandas import DataFrame, Series, concat
from pandas.testing import assert_frame_equal
from sortedcontainers import SortedDict

from syphon.archive import datafilter

from .. import make_dataframe

MAX_ROWS = 10
MAX_COLS = 5


class TestDataFilter(object):
    fail_message = "Could not find a matching frame in the filtered list."

    def _build_dataframes(
        self,
        frame: DataFrame,
        meta_cvals: Dict[str, List[str]],
        keylist: List[str],
        data: List[DataFrame] = [],
    ) -> List[DataFrame]:
        result = data.copy()

        this_keylist: List[str] = keylist.copy()
        this_keylist.reverse()
        try:
            header: str = this_keylist.pop()
        except IndexError:
            result.append(frame)
            return result

        if len(meta_cvals[header]) == 0:
            return result

        for val in meta_cvals[header]:
            rows, _ = frame.shape
            new_col = Series([val] * rows, name=header)
            this_frame: DataFrame = concat([frame.copy(), new_col], axis=1)
            result = self._build_dataframes(
                this_frame, meta_cvals, this_keylist, data=result
            )
        return result

    def _test_dataframes(
        self, rows: int, cols: int, meta_cvals: Dict[str, List[str]]
    ) -> Tuple[List[DataFrame], List[DataFrame]]:
        """Return tuple is (expected, actual)."""
        data: DataFrame = make_dataframe(rows, cols)
        meta_col_vals: Dict[str, List[str]] = meta_cvals.copy()
        keys: List[str] = list(meta_cvals.keys())

        expected: List[DataFrame] = self._build_dataframes(data, meta_col_vals, keys)

        schema = SortedDict()
        index = 0
        for k in keys:
            schema[str(index)] = k
            index += 1

        alldata = DataFrame()
        if len(expected) == 0:
            alldata = data.copy()
        else:
            for f in expected:
                alldata = concat([alldata, f])
            alldata.reset_index(drop=True, inplace=True)

        actual: List[DataFrame] = datafilter(schema, alldata)

        return (expected, actual)

    @pytest.mark.less_coverage
    def test_datafilter_fixed_uniform_meta(
        self, metadata_columns: Dict[str, List[str]]
    ):
        expected, actual = self._test_dataframes(MAX_ROWS, MAX_COLS, metadata_columns)

        if len(expected) is len(actual):
            assert True
            return

        for e in expected:
            match: Optional[DataFrame] = None
            for a in actual:
                if e.equals(a):
                    match = a.copy()
                    break
            if match is not None:
                assert_frame_equal(e, match)
            else:
                pytest.fail(TestDataFilter.fail_message)

    @pytest.mark.less_coverage
    def test_datafilter_fixed_uneven_meta(
        self, metadata_random_columns: Dict[str, List[str]]
    ):
        expected, actual = self._test_dataframes(
            MAX_ROWS, MAX_COLS, metadata_random_columns
        )

        if len(expected) is len(actual):
            assert True
            return

        for e in expected:
            match: Optional[DataFrame] = None
            for a in actual:
                if e.equals(a):
                    match = a.copy()
                    break
            if match is not None:
                assert_frame_equal(e, match)
            else:
                pytest.fail(TestDataFilter.fail_message)

    @pytest.mark.slow
    @pytest.mark.parametrize("rows", [r for r in range(1, MAX_ROWS + 1)])
    @pytest.mark.parametrize("cols", [c for c in range(1, MAX_COLS + 1)])
    def test_datafilter_uniform_metadata(
        self, rows: int, cols: int, metadata_columns: Dict[str, List[str]]
    ):
        expected, actual = self._test_dataframes(rows, cols, metadata_columns)

        if len(expected) is len(actual):
            assert True
            return

        for e in expected:
            match: Optional[DataFrame] = None
            for a in actual:
                if e.equals(a):
                    match = a.copy()
                    break
            if match is not None:
                assert_frame_equal(e, match)
            else:
                pytest.fail(TestDataFilter.fail_message)

    @pytest.mark.slow
    @pytest.mark.parametrize("rows", [r for r in range(1, MAX_ROWS + 1)])
    @pytest.mark.parametrize("cols", [c for c in range(1, MAX_COLS + 1)])
    def test_datafilter_uneven_metadata(
        self, rows: int, cols: int, metadata_random_columns: Dict[str, List[str]]
    ):
        expected, actual = self._test_dataframes(rows, cols, metadata_random_columns)

        if len(expected) is len(actual):
            assert True
            return

        for e in expected:
            match: Optional[DataFrame] = None
            for a in actual:
                if e.equals(a):
                    match = a.copy()
                    break
            if match is not None:
                assert_frame_equal(e, match)
            else:
                pytest.fail(TestDataFilter.fail_message)
