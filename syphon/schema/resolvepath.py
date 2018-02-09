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
        IndexError: Schema value is not a column header of the given
            DataFrame.
        ValueError: When a column corresponding to a `SortedDict` entry
            contains more than one value.
    """
    from os.path import join

    result = archive

    for key in schema:
        header = schema[key]
        if header not in list(datapool.columns):
            raise IndexError('Schema value {} is not a column in the current '
                             'DataFrame.'.format(header))
        if len(datapool.get(header).drop_duplicates().values) > 1:
            raise ValueError('More than one value exists under the {} column.'
                             .format(header))
        # faster than calling datapool.get(header)...values again
        value = datapool.get(header).iloc[0]
        result = join(result, _normalize(value))

    return result
