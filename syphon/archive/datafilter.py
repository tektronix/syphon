"""syphon.archive.datafilter.py

   Copyright Keithley Instruments, LLC.
   Licensed under MIT (https://github.com/tektronix/syphon/blob/master/LICENSE)

"""
from typing import List, Optional

from pandas import DataFrame
from sortedcontainers import SortedDict


def _datafilter(
    schema: SortedDict, datapool: DataFrame, filtered: Optional[List[DataFrame]] = None
) -> List[DataFrame]:
    """The `filtered` parameter should only be used internally."""
    result: List[DataFrame] = [] if filtered is None else filtered.copy()

    this_schema: SortedDict = schema.copy()
    try:
        _, header = this_schema.popitem(last=False)
    except KeyError:
        result.append(datapool)
        return result

    if header not in datapool.columns:
        return result

    for value in datapool.get(header).drop_duplicates().values:
        new_pool: DataFrame = datapool.loc[datapool.get(header) == value]
        result = _datafilter(this_schema, new_pool, filtered=result)
    return result


def datafilter(schema: SortedDict, datapool: DataFrame) -> List[DataFrame]:
    """Splits a `DataFrame` into a `DataFrame` list based on schema
    values.

    Each `DataFrame` object in the list will have a single value for all
    schema columns.

    Args:
        schema (SortedDict): Column names to use for filtering.
        datapool (DataFrame): Data to filter.

    Returns:
        list: The filtered DataFrame objects. An empty list is
            returned if no schema values could be found.
    """
    return _datafilter(schema, datapool)
