"""syphon.rebuild.rebuild.py

   Copyright (c) 2017-2018 Keithley Instruments, LLC.
   Licensed under MIT (https://github.com/ehall/syphon/blob/master/LICENSE)

"""
from syphon import Context

def rebuild(context: Context):
    """Combine all archived data files into a single file.

    Args:
        context (Context): Runtime settings object.
    """
    from os import walk
    from os.path import join

    from pandas import DataFrame, read_csv

    file_list = list()

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
        except:
            raise
        else:
            cache.reset_index(drop=True, inplace=True)

    try:
        cache.to_csv(context.cache, index=False)
    except:
        raise
