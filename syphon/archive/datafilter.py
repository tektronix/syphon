"""syphon.archive.datafilter.py

   Copyright (c) 2017-2018 Keithley Instruments, LLC.
   Licensed under MIT (https://github.com/ehall/syphon/blob/master/LICENSE)

"""
from pandas import DataFrame
from sortedcontainers import SortedDict

def _datafilter(schema: SortedDict, datapool: DataFrame, filtered=[]) -> list:
    """The `filtered` parameter should only be used internally."""
    this_schema = schema.copy()
    header = None
    try:
        _, header = this_schema.popitem(last=False)
    except KeyError:
        filtered.append(datapool)
        return filtered
    except:
        raise

    for value in datapool.get(header).drop_duplicates().values:
        new_pool = datapool.loc[datapool.get(header) == value]
        try:
            filtered = _datafilter(this_schema, new_pool, filtered=filtered)
        except:
            raise
    return filtered

def datafilter(schema: SortedDict, datapool: DataFrame) -> list:
    """Splits a `DataFrame` into a `DataFrame` list based on schema values.

    Each `DataFrame` object in the list will have a single value for all
    schema columns.

    Args:
        schema (SortedDict): Column names to use for filtering.
        datapool (DataFrame): Data to filter.

    Returns:
        list: The filtered `DataFrame` objects.
    """
    try:
        return _datafilter(schema, datapool)
    except:
        raise
