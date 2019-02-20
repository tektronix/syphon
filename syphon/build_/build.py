"""syphon.build_.build.py

   Copyright Keithley Instruments, LLC.
   Licensed under MIT (https://github.com/tektronix/syphon/blob/master/LICENSE)

"""
from syphon import Context


def build(context: Context):
    """Combine all archived data files into a single file.

    Args:
        context (Context): Runtime settings object.

    Raises:
        OSError: File operation error. Error type raised may be
            a subclass of OSError.
        FileExistsError: Cache file exists and overwrite is
            False.
    """
    from os import walk
    from os.path import exists, join

    from pandas import DataFrame, read_csv

    file_list = list()

    if exists(context.cache) and not context.overwrite:
        raise FileExistsError('Cache file already exists')

    for root, _, files in walk(context.archive):
        for f in files:
            # skip linux-style hidden files
            if f[0] is not '.':
                file_list.append(join(root, f))

    cache = DataFrame()
    for file in file_list:
        try:
            data = DataFrame(read_csv(file, dtype=str))
            cache = cache.append(data)
        except OSError:
            raise
        else:
            cache.reset_index(drop=True, inplace=True)

    try:
        cache.to_csv(context.cache, index=False)
    except OSError:
        raise
