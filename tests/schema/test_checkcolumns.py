"""syphon.tests.schema.test_checkcolumns.py

   Copyright Keithley Instruments, LLC.
   Licensed under MIT (https://github.com/tektronix/syphon/blob/master/LICENSE)

"""
import pytest
from pandas import DataFrame, read_csv
from pandas.compat import StringIO
from sortedcontainers import SortedDict

from syphon.schema import check_columns


class TestCheckColumns(object):
    multi_column = "column1,column2,column3,column4"
    multi_schema = SortedDict({"0": "column2", "1": "column4"})
    multi_schema2 = SortedDict({"0": "column1", "1": "column3", "2": "column4"})
    multi_schema3 = SortedDict({"0": "column2", "1": "column7"})

    single_column = "column1"
    single_schema = SortedDict({"0": "column1"})
    single_schema2 = SortedDict({"0": "column5"})

    @pytest.mark.parametrize(
        "schema, data",
        [
            (single_schema, DataFrame(read_csv(StringIO(single_column)))),
            (single_schema, DataFrame(read_csv(StringIO(multi_column)))),
            (multi_schema, DataFrame(read_csv(StringIO(multi_column)))),
            (multi_schema2, DataFrame(read_csv(StringIO(multi_column)))),
        ],
    )
    def test_check_columns_pass(self, schema: SortedDict, data: DataFrame):
        try:
            check_columns(schema, data)
        except IndexError:
            pytest.fail()

    @pytest.mark.parametrize(
        "schema, data",
        [
            (single_schema2, DataFrame(read_csv(StringIO(single_column)))),
            (single_schema2, DataFrame(read_csv(StringIO(multi_column)))),
            (multi_schema, DataFrame(read_csv(StringIO(single_column)))),
            (multi_schema2, DataFrame(read_csv(StringIO(single_column)))),
            (multi_schema3, DataFrame(read_csv(StringIO(multi_column)))),
        ],
    )
    def test_check_columns_fail(self, schema: SortedDict, data: DataFrame):
        with pytest.raises(IndexError):
            check_columns(schema, data)
