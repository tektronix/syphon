"""syphon.core.archive.filemap.py

   Copyright Keithley Instruments, LLC.
   Licensed under MIT (https://github.com/tektronix/syphon/blob/master/LICENSE)

"""
import os
from enum import Enum
from typing import Dict, List


class MappingBehavior(Enum):
    ONE_TO_ONE = 0
    ONE_TO_MANY = 1


def filemap(
    behavior: MappingBehavior, data: List[str], meta: List[str]
) -> Dict[str, List[str]]:
    """Create a data-metadata file pair map.

    If the given behavior is one-to-one, then match each data file with
    a metadata file that has the same name (excluding the extension).

    If the given behavior is one-to-many, then each data file will
    match to all metadata files.

    Args:
        behavior: How data and metadata files should be mapped.
        data: Absolute data file paths.
        meta: Absolute metadata file paths.

    Returns:
        Dictionary containing string keys which index string lists.

        Keys are the given data files.
        Each value is a list containing metadata files associated with
        the data file key.

        Empty if the requested behavior could not be performed on the
        given file lists.
    """
    result: Dict[str, List[str]] = dict()

    if behavior == MappingBehavior.ONE_TO_ONE and len(data) == len(meta):
        # Associate one data file to a matching metadata file.
        for datafile in data:
            dataname, _ = os.path.splitext(os.path.basename(datafile))
            for metafile in meta:
                metaname, _ = os.path.splitext(os.path.basename(metafile))
                if dataname == metaname:
                    result[datafile] = [metafile]

    elif behavior == MappingBehavior.ONE_TO_MANY:
        # Associate each data file to all metadata files.
        for datafile in data:
            result[datafile] = [metafile for metafile in meta]

    return result
