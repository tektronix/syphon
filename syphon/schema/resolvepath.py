"""syphon.schema.resolvepath.py

   Copyright (c) 2017-2018 Keithley Instruments, LLC.
   Licensed under MIT (https://github.com/ehall/syphon/blob/master/LICENSE)

"""
from pandas import DataFrame
from syphon.common import Context

def _normalize(directory: str) -> str:
    """Make lowercase and replace spaces with underscores."""
    directory = directory.lower()
    directory = directory.replace(' ', '_')
    return directory

def resolve_path(context: Context, datapool: DataFrame) -> str:
    """Use the given context and dataset to make a path.

    The base path is `Context.archive`. Additional directories are appended
    for the value of each `Context.schema` entry in the given `DataFrame`.

    It is important that columns corresponding to a `Context.schema` entry
    contain a single value.

    Args:
        context (Context): Runtime settings object.
        datapool (DataFrame): Data to use during path resolution.

    Return:
        str: The resolved path.

    Raises:
        ValueError: A column corresponding to a `Context.schema` entry
            contains more than one value.
    """
    from os.path import join

    result = context.archive

    for key in context.schema:
        header = context.schema[key]
        if len(datapool.get(header).drop_duplicates().values) > 1:
            raise ValueError('More than one value exists under the {} column.'
                             .format(header))
        # faster than calling datapool.get(header)...values again
        value = datapool.get(header).iloc[0]
        result = join(result, _normalize(value))

    return result
