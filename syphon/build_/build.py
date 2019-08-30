"""syphon.build_.build.py

   Copyright Keithley Instruments, LLC.
   Licensed under MIT (https://github.com/tektronix/syphon/blob/master/LICENSE)

"""
from syphon import Context

LINUX_HIDDEN_CHAR: str = "."


def build(context: Context):
    """Combine all archived data files into a single file.

    Args:
        context (Context): Runtime settings object.

    Raises:
        AssertionError: Context.cache or Context.archive is None.
        OSError: File operation error. Error type raised may be
            a subclass of OSError.
        FileExistsError: Cache file exists and overwrite is
            False.
    """
    from os import walk
    from os.path import exists, join
    from typing import Tuple

    from pandas import DataFrame, read_csv

    file_list = list()

    if context.cache is None:
        raise AssertionError()
    if exists(context.cache) and not context.overwrite:
        raise FileExistsError("Cache file already exists")

    if context.archive is None:
        raise AssertionError()
    for root, _, files in walk(context.archive):
        for file in files:
            # skip linux-style hidden files
            if file[0] is not LINUX_HIDDEN_CHAR:
                file_list.append(join(root, file))

    cache = DataFrame()
    for file in file_list:
        if context.verbose:
            print("Build: from {0}".format(file))

        data = DataFrame(read_csv(file, dtype=str))

        if context.verbose:
            data_shape: Tuple[int, int] = data.shape
            cache_pre_shape: Tuple[int, int] = cache.shape

        cache = cache.append(data)

        if context.verbose:
            print(
                "Build: appending data {0} onto cache {1} => {2}".format(
                    data_shape, cache_pre_shape, cache.shape
                )
            )

        cache.reset_index(drop=True, inplace=True)

    cache.to_csv(context.cache, index=False)

    if context.verbose:
        print("Build: wrote {0}".format(context.cache))
