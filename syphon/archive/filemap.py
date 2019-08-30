"""syphon.archive.filemap.py

   Copyright Keithley Instruments, LLC.
   Licensed under MIT (https://github.com/tektronix/syphon/blob/master/LICENSE)

"""
from typing import Optional

from sortedcontainers import SortedDict, SortedList


def _multi_map(data: SortedList, meta: SortedList) -> SortedDict:
    """Pair all metadata files to each data file."""
    result: SortedDict = SortedDict()

    for dataname in data:
        result[dataname] = [metaname for metaname in meta]

    return result


def _name_map(data: SortedList, meta: SortedList) -> Optional[SortedDict]:
    """Pair each data and metadata file by filename.

    Returns `None` is there was a data-metadata filename mismatch.
    """

    def _get_name(filepath: str) -> str:
        """Get the filename without the path or extension."""
        from os.path import split, splitext

        _, full_name = split(filepath)
        name, _ = splitext(full_name)
        return name

    result: SortedDict = SortedDict()
    target_length: int = len(data)

    for dataname in data:
        name: str = _get_name(dataname)
        for metaname in meta:
            if name == _get_name(metaname):
                result[dataname] = [metaname]

    if len(result.keys()) is not target_length:
        return None

    return result


def file_map(data: SortedList, meta: SortedList) -> SortedDict:
    """Create a data-metadata file pair map.

    If there are more data files than metadata files (or vise versa),
    then each data file will match to all metadata files.

    If there are equal number data and metadata files, then try to match
    each data file with a metadata file that has the same name
    (excluding the extension). If there is not a match for every data
    file, then revert to the previous matching scheme.

    Args:
        data (SortedList): Ordered list of absolute data file
            paths.
        meta (SortedList): Ordered list of absolute metadata
            file paths.

    Returns:
        SortedDict: Dictionary sorted by key which indexes
            string lists.

        Keys are the absolute file path of a data file as a
        string. Values are a string list containing the absolute
        file path of metadata files associated with a data file.
    """
    result = None

    if len(data) == len(meta):
        result = _name_map(data, meta)

    if result is None:
        result = _multi_map(data, meta)

    return result
