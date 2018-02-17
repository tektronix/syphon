"""syphon.tests.archive.test_datafilter.py

   Copyright (c) 2017-2018 Keithley Instruments, LLC.
   Licensed under MIT (https://github.com/ehall/syphon/blob/master/LICENSE)

"""
import random
from os import environ

import pytest
from pandas import concat, DataFrame, Series
from pandas.testing import assert_frame_equal
from pandas.util.testing import makeCustomIndex
from sortedcontainers import SortedDict
from syphon.archive import datafilter

from .. import make_dataframe

MAX_ROWS = 10
MAX_COLS = 5

class TestDataFilter(object):
    def _build_dataframes(self, frame: DataFrame,
                          meta_cvals: dict,
                          keylist: list,
                          result=None) -> list:
        if result is None:
            result = []

        this_keylist = keylist.copy()
        this_keylist.reverse()
        header = None
        try:
            header = this_keylist.pop()
        except IndexError:
            result.append(frame)
            return result
        except:
            raise

        if len(meta_cvals[header]) is 0:
            return result

        for val in meta_cvals[header]:
            rows, _ = frame.shape
            new_col = Series([val]*rows, name=header)
            this_frame = concat([frame.copy(), new_col], axis=1)
            try:
                result = self._build_dataframes(this_frame, meta_cvals,
                                                this_keylist, result=result)
            except:
                raise
        return result

    def _test_dataframes(self, rows, cols, meta_cvals) -> (list, list):
        """Return tuple is (expected, actual)."""
        data = make_dataframe(rows, cols)
        meta_col_vals = meta_cvals.copy()
        keys = list(meta_cvals.keys())

        expected = self._build_dataframes(data, meta_col_vals, keys)

        schema = SortedDict()
        index = 0
        for k in keys:
            schema[str(index)] = k
            index += 1

        alldata = DataFrame()
        if len(expected) is 0:
            alldata = data.copy()
        else:
            for f in expected:
                alldata = concat([alldata, f])
            alldata.reset_index(drop=True, inplace=True)

        actual = datafilter(schema, alldata)

        return (expected, actual)

    @pytest.mark.less_coverage
    def test_datafilter_fixed_uniform_meta(self, metadata_columns):
        expected, actual = self._test_dataframes(MAX_ROWS, MAX_COLS,
                                                 metadata_columns)

        if len(expected) is len(actual):
            assert True
            return

        for e in expected:
            match = None
            for a in actual:
                if e.equals(a):
                    match = a.copy()
                    break
            if match is not None:
                assert_frame_equal(e, match)
            else:
                msg='Could not find a matching frame in the filtered list.'
                pytest.fail(msg=msg)

    @pytest.mark.less_coverage
    def test_datafilter_fixed_uneven_meta(self, metadata_random_columns):
        expected, actual = self._test_dataframes(MAX_ROWS, MAX_COLS,
                                                 metadata_random_columns)

        if len(expected) is len(actual):
            assert True
            return

        for e in expected:
            match = None
            for a in actual:
                if e.equals(a):
                    match = a.copy()
                    break
            if match is not None:
                assert_frame_equal(e, match)
            else:
                msg='Could not find a matching frame in the filtered list.'
                pytest.fail(msg=msg)

    @pytest.mark.slow
    @pytest.mark.parametrize('rows', [r for r in range(1, MAX_ROWS + 1)])
    @pytest.mark.parametrize('cols', [c for c in range(1, MAX_COLS + 1)])
    def test_datafilter_uniform_metadata(self, rows, cols, metadata_columns):
        expected, actual = self._test_dataframes(rows, cols, metadata_columns)

        if len(expected) is len(actual):
            assert True
            return

        for e in expected:
            match = None
            for a in actual:
                if e.equals(a):
                    match = a.copy()
                    break
            if match is not None:
                assert_frame_equal(e, match)
            else:
                msg='Could not find a matching frame in the filtered list.'
                pytest.fail(msg=msg)

    @pytest.mark.slow
    @pytest.mark.parametrize('rows', [r for r in range(1, MAX_ROWS + 1)])
    @pytest.mark.parametrize('cols', [c for c in range(1, MAX_COLS + 1)])
    def test_datafilter_uneven_metadata(self, rows, cols,
                                        metadata_random_columns):
        expected, actual = self._test_dataframes(rows, cols,
                                                 metadata_random_columns)

        if len(expected) is len(actual):
            assert True
            return

        for e in expected:
            match = None
            for a in actual:
                if e.equals(a):
                    match = a.copy()
                    break
            if match is not None:
                assert_frame_equal(e, match)
            else:
                msg='Could not find a matching frame in the filtered list.'
                pytest.fail(msg=msg)
