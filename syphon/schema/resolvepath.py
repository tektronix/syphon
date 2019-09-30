"""syphon.schema.resolvepath.py

   Copyright Keithley Instruments, LLC.
   Licensed under MIT (https://github.com/tektronix/syphon/blob/master/LICENSE)

"""
from pandas import DataFrame
from sortedcontainers import SortedDict


def _normalize(directory: str) -> str:
    """Make lowercase and replace spaces with underscores."""
    result: str = directory.lower()
    result = result.replace(" ", "_")
    if result[-1] == ".":
        result = result[:-1]
    return result


def resolve_path(archive: str, schema: SortedDict, datapool: DataFrame) -> str:
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
            For best results, ensure all dtypes are strings.

    Return:
        str: The resolved path.

    Raises:
        IndexError: Schema value is not a column header of the
            given DataFrame.
        ValueError: When a column corresponding to a SortedDict
            entry contains more than one value.
    """
    from os.path import join
    from typing import Any, List

    from numpy import nan

    result: str = archive

    for key in schema:
        header: str = schema[key]
        if header not in list(datapool.columns):
            raise IndexError(
                "Schema value {} is not a column in the current DataFrame.".format(
                    header
                )
            )
        row_values: List[Any] = list(datapool.get(header).drop_duplicates().values)
        if nan in row_values:
            row_values.remove(nan)
        if "" in row_values:
            row_values.remove("")
        if len(row_values) > 1:
            raise ValueError(
                "More than one value exists under the {} column.".format(header)
            )
        value: Any = row_values.pop()
        result = join(result, _normalize(str(value)))

    return result
