"""syphon.core.archive.datafilter.py

   Copyright Keithley Instruments, LLC.
   Licensed under MIT (https://github.com/tektronix/syphon/blob/master/LICENSE)

"""
from typing import List

from pandas import DataFrame
from sortedcontainers import SortedDict


def datafilter(schema: SortedDict, datapool: DataFrame, **kwargs) -> List[DataFrame]:
    """Splits a DataFrame based on the value of applicable columns.

    Each DataFrame object in the returned list will have a single value for
    those columns contained in the schema.

    Args:
        schema: Column names to use for filtering.
        datapool: Data to filter.

    Returns:
        The filtered DataFrame objects. An empty list is returned if no schema
        values could be found.
    """
    result: List[DataFrame] = kwargs["filtered"].copy() if "filtered" in kwargs else []

    this_schema: SortedDict = schema.copy()
    try:
        _, header = this_schema.popitem(index=0)
    except KeyError:
        result.append(datapool)
        return result

    if header not in datapool.columns:
        return result

    for value in datapool.get(header).drop_duplicates().values:
        new_pool: DataFrame = datapool.loc[datapool.get(header) == value]
        result = datafilter(this_schema, new_pool, filtered=result)
    return result
