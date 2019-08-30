"""syphon.schema.load.py

   Copyright Keithley Instruments, LLC.
   Licensed under MIT (https://github.com/tektronix/syphon/blob/master/LICENSE)

"""
from sortedcontainers import SortedDict


def load(filepath: str) -> SortedDict:
    """Return a `SortedDict` from a schema file.

    Args:
        filepath (str): Absolute filename of the schema file.

    Returns:
        SortedDict: Ordered archive directory storage schema.

    Raises:
        OSError: File operation error. Error type raised may be
            a subclass of OSError.
    """
    from json import loads

    result: SortedDict = SortedDict()
    with open(filepath, "r", encoding="utf-8") as file:
        result = SortedDict(loads(file.read()))

    return result
