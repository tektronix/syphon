"""syphon.archive.archive.py

   Copyright (c) 2017-2018 Keithley Instruments, LLC.
   Licensed under MIT (https://github.com/ehall/syphon/blob/master/LICENSE)

"""
from syphon.common import Context

def archive(context: Context):
    """Store the files specified in the current context.

    Args:
        context (Context): Runtime settings object.
    """
    from glob import glob
    from os import makedirs
    from os.path import join, split

    from pandas import concat, DataFrame, read_csv, Series
    from pandas.errors import EmptyDataError
    from sortedcontainers import SortedList
    from syphon.schema import check_columns, resolve_path

    from . import datafilter
    from . import file_map
    from . import LockManager

    lock_manager = LockManager()
    lock_list = list()

    data_list = SortedList(glob(context.data))
    try:
        lock_list.append(lock_manager.lock(split(data_list[0])[0]))
    except:
        raise

    meta_list = SortedList()
    if context.meta is not None:
        meta_list = SortedList(glob(context.meta))
        try:
            lock_list.append(lock_manager.lock(split(meta_list[0])[0]))
        except:
            raise

    fmap = file_map(data_list, meta_list)

    for datafile in fmap:
        _, datafilename = split(datafile)

        data_frame = None
        try:
            #TODO: Issue #9 - 'open file' abstractions here
            data_frame = DataFrame(read_csv(datafile, dtype=str))
        except EmptyDataError:
            # trigger the empty check below
            data_frame = DataFrame()
        except:
            raise

        if data_frame.empty:
            print('Skipping empty data file @ {}'.format(datafile))
            continue

        # remove empty columns
        data_frame.dropna(axis=1, how='all', inplace=True)

        total_rows, _ = data_frame.shape

        # merge all metadata files into a single DataFrame
        meta_frame = None
        for metafile in fmap[datafile]:
            try:
                #TODO: Issue #9 - 'open file' abstractions here
                new_frame = DataFrame(read_csv(metafile, dtype=str))
            except:
                raise

            new_frame.dropna(axis=1, how='all', inplace=True)
            for header in list(new_frame.columns.values):
                # complain if there's more than one value in a column
                if len(new_frame[header].drop_duplicates().values) > 1:
                    raise ValueError('More than one value exists under '
                                        'the {} column.'.format(header))

                if len(new_frame[header]) is total_rows:
                    if meta_frame is None:
                        meta_frame = new_frame[header]
                    else:
                        meta_frame = concat([meta_frame, new_frame[header]], axis=1)
                else:
                    meta_value = new_frame[header].iloc[0]
                    series = Series([meta_value] * total_rows, name=header)
                    if meta_frame is None:
                        meta_frame = DataFrame(series)
                    else:
                        meta_frame = concat([meta_frame, series], axis=1)

        if meta_frame is not None:
            data_frame = concat([data_frame, meta_frame], axis=1)

        try:
            check_columns(context.schema, data_frame)
        except:
            raise

        filtered_data = None
        try:
            filtered_data = datafilter(context.schema, data_frame)
        except:
            raise

        for data in filtered_data:
            path = None
            try:
                path = resolve_path(context, data)
                makedirs(path, exist_ok=True)
                data.to_csv(join(path, datafilename), index=False)
            except:
                raise

    while len(lock_list) > 0:
        lock = lock_list.pop()
        try:
            lock_manager.release(lock)
        except:
            raise
