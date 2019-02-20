"""syphon.schema.save.py

   Copyright Keithley Instruments, LLC.
   Licensed under MIT (https://github.com/ehall/syphon/blob/master/LICENSE)

"""
from sortedcontainers import SortedDict


def save(schema: SortedDict, filepath: str, overwrite: bool):
    """Save a `SortedDict` as a schema file.

    Args:
        schema (SortedDict): Archive directory storage schema.
        filepath (str): Absolute filename of the schema file.
        overwrite (bool): True to overwrite existing file.

    Raises:
        OSError: File operation error. Error type raised may be
            a subclass of OSError.
        FileExistsError: Schema file exists and overwrite is
            False.
    """
    from json import dumps
    from os import remove
    from os.path import exists

    if exists(filepath) and overwrite:
        try:
            remove(filepath)
        except OSError:
            raise
    elif exists(filepath) and not overwrite:
        raise FileExistsError('Schema file already exists')

    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(dumps(schema, indent=2))
    except OSError:
        raise
    else:
        return
