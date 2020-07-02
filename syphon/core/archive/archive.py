"""syphon.core.archive.archive.py

   Copyright Keithley Instruments, LLC.
   Licensed under MIT (https://github.com/tektronix/syphon/blob/master/LICENSE)

"""
import os
from typing import Dict, List, Optional, Set

from pandas import DataFrame, Series, concat, read_csv
from sortedcontainers import SortedDict

from ... import schema as schema_help
from ...errors import InconsistentMetadataError
from .datafilter import datafilter
from .filemap import MappingBehavior, filemap
from .lockmanager import LockManager


def merge_metafiles(
    filemap: Dict[str, List[str]], datafile: str, data_rows: int
) -> Optional[DataFrame]:
    # merge all metadata files into a single DataFrame
    meta_frame = DataFrame()
    for metafile in filemap[datafile]:
        new_frame = DataFrame(read_csv(metafile, dtype=str))

        new_frame.dropna(axis=1, how="all", inplace=True)
        for header in list(new_frame.columns.values):
            # complain if there's more than one value in a column
            if len(new_frame[header].drop_duplicates().values) > 1:
                raise InconsistentMetadataError(header)

            if len(new_frame[header]) is data_rows:
                meta_frame = concat([meta_frame, new_frame[header]], axis=1)
            else:
                meta_value = new_frame[header].iloc[0]
                series = Series([meta_value] * data_rows, name=header)
                meta_frame = concat([meta_frame, series], axis=1)

    return None if meta_frame.empty else meta_frame


def write_filtered_data(
    archive: str,
    schema: SortedDict,
    filtered_data: List[DataFrame],
    datafile: str,
    overwrite: bool,
    verbose: bool,
) -> List[str]:
    """Returns a list of written files."""
    datafilename = os.path.basename(datafile)

    written_files: List[str] = []
    for data in filtered_data:
        path: Optional[str] = None
        path = schema_help.resolve_path(archive, schema, data)

        target_filename: str = os.path.join(
            path, datafilename
        ) if path is not None else datafilename

        if os.path.exists(target_filename) and not overwrite:
            raise FileExistsError(f"File already exists in archive @ {target_filename}")

        os.makedirs(path, exist_ok=True)
        data.to_csv(target_filename, index=False)
        written_files.append(target_filename)
        if verbose:
            print(f"Archived {target_filename}")

    return written_files


def collate_data(
    archive_dir: str,
    data_list: List[str],
    meta_list: List[str],
    filemap_behavior: MappingBehavior,
    schema: SortedDict,
    overwrite: bool,
    verbose: bool,
) -> Dict[str, List[str]]:
    """Returns a dictionary containing string keys which index string lists.

    Keys are the given data files.
    Each value is a list of files collated and archived from the data file key.
    """
    from pandas.errors import EmptyDataError

    fmap: Dict[str, List[str]]
    collated_files: Dict[str, List[str]]
    if len(meta_list) > 0:
        fmap = filemap(filemap_behavior, data_list, meta_list)
        collated_files = {key: [] for key in data_list}
    else:
        fmap = {key: [] for key in data_list}
        collated_files = fmap.copy()

    for datafile in fmap.keys():
        try:
            data_frame = DataFrame(read_csv(datafile, dtype=str))
        except EmptyDataError:
            # trigger the empty check below
            data_frame = DataFrame()

        if data_frame.empty:
            if verbose:
                print(f"Skipping empty data file @ {datafile}")
            continue

        # remove empty columns
        data_frame.dropna(axis=1, how="all", inplace=True)

        try:
            meta_frame: Optional[DataFrame] = merge_metafiles(
                fmap, datafile, data_frame.shape[0]
            )
        except InconsistentMetadataError as err:
            raise ValueError(
                f'More than one value exists under the "{err.column}" column.'
            )

        if meta_frame is not None:
            data_frame = concat([data_frame, meta_frame], axis=1)

        schema_help.check_columns(schema, data_frame)

        filtered_data: List[DataFrame] = datafilter(schema, data_frame)

        collated_files[datafile] = write_filtered_data(
            archive_dir, schema, filtered_data, datafile, overwrite, verbose
        )

    return collated_files


def archive(
    archive_dir: str,
    data_files: List[str],
    meta_files: Optional[List[str]] = None,
    filemap_behavior: MappingBehavior = MappingBehavior.ONE_TO_ONE,
    schema_filepath: Optional[str] = None,
    cache_filepath: Optional[str] = None,
    hash_filepath: Optional[str] = None,
    overwrite: bool = False,
    verbose: bool = False,
) -> bool:
    # NOTE:
    # the build & check function use the exact same wording for "hash_filepath".
    """Collate and store the data files.

    Args:
        archive_dir: Absolute path to the data storage directory.
        data_files: CSV files to add to the archive.
        meta_files: CSV files to treat as metadata files.
        filemap_behavior: How data and metadata files should be mapped.
        schema_filepath: Absolute path to a JSON file containing a storage schema.
        cache_filepath: Absolute path to a build file to increment.
        hash_filepath: Path to a file containing a SHA256 sum of the cache. If not
            given, then the default is calculated by joining the cache directory with
            `syphon.core.check.DEFAULT_FILE`.
        overwrite: Whether existing files should be overwritten during archival.
        verbose: Whether activities should be printed to the standard output.

    Returns:
        True if the given files where archived successfully, False otherwise.
        If an increment_filepath is given, then this includes the status of the build
        command.

    Raises:
        FileExistsError: An archive file already exists with the same filepath.
        FileNotFoundError: A given file does not exist.
        IndexError: Schema value is not a column header of a given DataFrame.
        OSError: File operation error. Error type raised may be a subclass of OSError.
        ValueError: More than one unique metadata value exists under a column header.
        Exception: Any error raised by pandas.read_csv.
    """
    from ..build import build as syphon_build

    if meta_files is None:
        meta_files = []

    lock_manager = LockManager()
    lock_list: List[str] = list()

    if len(data_files) == 0:
        lock_manager.release_all()
        if verbose:
            print("Nothing to archive")
        return False

    schema = SortedDict()
    if schema_filepath is not None:
        if not os.path.exists(schema_filepath):
            raise FileNotFoundError(
                f"Cannot archive using nonexistent schema file @ {schema_filepath}"
            )
        schema = schema_help.load(schema_filepath)

    # add '#lock' file to all data directories
    for d_file in data_files:
        if not os.path.exists(d_file):
            lock_manager.release_all()
            raise FileNotFoundError(f"Cannot archive nonexistent data file @ {d_file}")
        lock_list.append(lock_manager.lock(os.path.dirname(d_file)))

    # add '#lock' file to all metadata directories
    for m_file in meta_files:
        if not os.path.exists(m_file):
            lock_manager.release_all()
            raise FileNotFoundError(
                f"Cannot archive nonexistent metadata file @ {m_file}"
            )
        lock_list.append(lock_manager.lock(os.path.dirname(m_file)))

    try:
        archival_map: Dict[str, List[str]] = collate_data(
            archive_dir,
            data_files,
            meta_files,
            filemap_behavior,
            schema,
            overwrite,
            verbose,
        )
    finally:
        lock_manager.release_all()

    newly_archived: Set[str] = set()
    for v in archival_map.values():
        # Each data file must have at least 1 corresponding archive file.
        if len(v) == 0:
            return False
        newly_archived.update(set(v))

    if cache_filepath is None:
        return True

    return syphon_build(
        cache_filepath,
        *newly_archived,
        hash_filepath=hash_filepath,
        incremental=True,
        overwrite=True,
        post_hash=True,
        verbose=verbose,
    )
