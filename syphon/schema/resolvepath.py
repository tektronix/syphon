"""syphon.schema.resolvepath.py

   Copyright (c) 2017-2018 Keithley Instruments, LLC.
   Licensed under MIT (https://github.com/ehall/syphon/blob/master/LICENSE)

"""
from pandas import DataFrame
from sortedcontainers import SortedDict


def _normalize(directory: str) -> str:
    """Make lowercase and replace spaces with underscores."""
    directory = directory.lower()
    directory = directory.replace(' ', '_')
    if directory[-1] == '.':
        directory = directory[:-1]
    return directory


def resolve_path(
        archive: str, schema: SortedDict, datapool: DataFrame) -> str:
    """Use the given schema and dataset to make a path.

    The base path is `archive`. Additional directories are appended
    for the value of each `SortedDict` entry in the given `DataFrame`.

    It is important that columns corresponding to a `SortedDict` entry
    contain a single value. A `ValueError` will be raised if more than
    one value exists in a target column.

    Args:
        archive (str): Directory where data is stored.
        schema (SortedDict): Archive directory storage schema.
        datapool (DataFrame): Data to use during path resolution.

    Return:
        str: The resolved path.

    Raises:
        IndexError: Schema value is not a column header of the
            given DataFrame.
        ValueError: When a column corresponding to a SortedDict
            entry contains more than one value.
    """
    from os.path import join

    from numpy import nan

    result = archive

    for key in schema:
        header = schema[key]
        if header not in list(datapool.columns):
            raise IndexError(
                'Schema value {} is not a column in the current DataFrame.'
                .format(header))
        row_values = list(datapool.get(header).drop_duplicates().values)
        if nan in row_values:
            row_values.remove(nan)
        if len(row_values) > 1:
            raise ValueError(
                'More than one value exists under the {} column.'
                .format(header))
        value = row_values.pop()
        result = join(result, _normalize(value))

    return result
