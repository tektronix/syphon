"""syphon.schema.checkcolumns.py

   Copyright Keithley Instruments, LLC.
   Licensed under MIT (https://github.com/tektronix/syphon/blob/master/LICENSE)

"""
from pandas import DataFrame
from sortedcontainers import SortedDict


def check_columns(schema: SortedDict, data: DataFrame):
    """Raises an error if a column header does not exist.

    Args:
        schema (SortedDict): Required column names.
        datapool (DataFrame): Data to check.

    Raises:
        IndexError: Schema value is not a column header of the
            given DataFrame.
    """
    from typing import List

    columns: List[str] = list(data.columns)
    for key in schema:
        header: str = schema[key]
        if header not in columns:
            raise IndexError('Cannot find schema-required column "{}"'.format(header))
