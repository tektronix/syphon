"""syphon.archive.archive.py

   Copyright Keithley Instruments, LLC.
   Licensed under MIT (https://github.com/tektronix/syphon/blob/master/LICENSE)

"""
from os.path import split
from typing import List, Optional

from pandas import DataFrame, Series, concat, read_csv
from pandas.errors import ParserError
from sortedcontainers import SortedDict

from syphon import Context

from ._lockmanager import LockManager


def _merge_metafiles(
    filemap: SortedDict, datafile: str, data_rows: int, lockman: LockManager
) -> Optional[DataFrame]:
    # merge all metadata files into a single DataFrame
    meta_frame = DataFrame()
    for metafile in filemap[datafile]:
        try:
            new_frame = DataFrame(read_csv(metafile, dtype=str))
        except ParserError:
            lockman.release_all()
            raise

        new_frame.dropna(axis=1, how="all", inplace=True)
        for header in list(new_frame.columns.values):
            # complain if there's more than one value in a column
            if len(new_frame[header].drop_duplicates().values) > 1:
                lockman.release_all()
                raise ValueError(
                    "More than one value exists under the {} column.".format(header)
                )

            if len(new_frame[header]) is data_rows:
                meta_frame = concat([meta_frame, new_frame[header]], axis=1)
            else:
                meta_value = new_frame[header].iloc[0]
                series = Series([meta_value] * data_rows, name=header)
                meta_frame = concat([meta_frame, series], axis=1)

    return None if meta_frame.empty else meta_frame


def _write_filtered_data(
    filtered_data: List[DataFrame],
    datafile: str,
    context: Context,
    lockman: LockManager,
):
    from os import makedirs
    from os.path import exists, join

    from syphon.schema import resolve_path

    _, datafilename = split(datafile)

    for data in filtered_data:
        path: Optional[str] = None
        try:
            if context.archive is None:
                raise AssertionError()
            path = resolve_path(context.archive, context.schema, data)
        except IndexError:
            lockman.release_all()
            raise
        except ValueError:
            lockman.release_all()
            raise

        target_filename: str = join(
            path, datafilename
        ) if path is not None else datafilename

        if exists(target_filename) and not context.overwrite:
            lockman.release_all()
            raise FileExistsError(
                "Archive error: file already exists @ " "{}".format(target_filename)
            )

        try:
            makedirs(path, exist_ok=True)
            data.to_csv(target_filename, index=False)
        except OSError:
            lockman.release_all()
            raise

        if context.verbose:
            print("Archive: wrote {0}".format(target_filename))


def archive(context: Context):
    """Store the files specified in the current context.

    Args:
        context (Context): Runtime settings object.

    Raises:
        AssertionError: Context.archive or Context.data is None.
        FileExistsError: An archive file already exists with
            the same filepath.
        IndexError: Schema value is not a column header of a
            given DataFrame.
        OSError: File operation error. Error type raised may be
            a subclass of OSError.
        ParserError: Error raised by pandas.read_csv.
        ValueError: More than one unique metadata value exists
            under a column header.
    """
    from glob import glob

    from pandas.errors import EmptyDataError
    from sortedcontainers import SortedList
    from syphon.schema import check_columns

    from . import datafilter
    from . import file_map

    lock_manager = LockManager()
    lock_list: List[str] = list()

    if context.data is None:
        raise AssertionError()
    # add '#lock' file to all data directories
    data_list: SortedList = SortedList(glob(context.data))
    lock_list.append(lock_manager.lock(split(data_list[0])[0]))

    # add '#lock' file to all metadata directories
    meta_list: SortedList = SortedList()
    if context.meta is not None:
        meta_list = SortedList(glob(context.meta))
        lock_list.append(lock_manager.lock(split(meta_list[0])[0]))

    fmap: SortedDict = file_map(data_list, meta_list)

    for datafile in fmap:
        try:
            data_frame = DataFrame(read_csv(datafile, dtype=str))
        except EmptyDataError:
            # trigger the empty check below
            data_frame = DataFrame()
        except ParserError:
            lock_manager.release_all()
            raise
        except Exception:
            raise

        if data_frame.empty:
            print("Skipping empty data file @ {}".format(datafile))
            continue

        # remove empty columns
        data_frame.dropna(axis=1, how="all", inplace=True)

        meta_frame: Optional[DataFrame] = _merge_metafiles(
            fmap, datafile, data_frame.shape[0], lock_manager
        )

        if meta_frame is not None:
            data_frame = concat([data_frame, meta_frame], axis=1)

        try:
            check_columns(context.schema, data_frame)
        except IndexError:
            lock_manager.release_all()
            raise

        filtered_data: List[DataFrame] = datafilter(context.schema, data_frame)

        if len(filtered_data) == 0:
            filtered_data = [data_frame]

        _write_filtered_data(filtered_data, datafile, context, lock_manager)

    while lock_list:
        lock: str = lock_list.pop()
        lock_manager.release(lock)
