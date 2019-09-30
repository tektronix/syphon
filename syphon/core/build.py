"""syphon.core.build.py

   Copyright Keithley Instruments, LLC.
   Licensed under MIT (https://github.com/tektronix/syphon/blob/master/LICENSE)

"""
from typing import Optional

LINUX_HIDDEN_CHAR: str = "."


def build(
    cache_filepath: str,
    *files: str,
    hash_filepath: Optional[str] = None,
    incremental: bool = False,
    overwrite: bool = False,
    post_hash: bool = True,
    verbose: bool = False,
) -> bool:
    # NOTE:
    # the archive & check function use the exact same wording for "hash_filepath".
    """Combine all archived data files into a single file.

    The value of the "incremental" argument is treated as False if the cache does not
    exist.

    Args:
        archive_dir: Absolute path to the data storage directory.
        cache_filepath: Absolute path to the target output file.
        *files: CSV files to combine.
        hash_filepath: Absolute path to a file containing a SHA256 sum of the
            cache. If not given, then the default is calculated by joining the cache
            directory with `syphon.core.check.DEFAULT_FILE`.
        incremental: Whether a build should be performed using an existing cache.
        overwrite: Whether an existing cache file should be replaced.
        post_hash: Whether to hash the cache upon completion.
        verbose: Whether activities should be printed to the standard output.

    Returns:
        True if successful, False otherwise.

    Raises:
        OSError: File operation error. Error type raised may be
            a subclass of OSError.
        FileExistsError: Cache file exists and overwrite is
            False.
    """
    import os
    from pathlib import Path
    from typing import Tuple

    from pandas import DataFrame, read_csv

    from ..hash import HashEntry, HashFile
    from .check import check
    from .check import DEFAULT_FILE as DEFAULT_HASH_FILE

    if len(files) == 0:
        if verbose:
            print("Nothing to build")
        return False

    if hash_filepath is None:
        cachepath, _ = os.path.split(cache_filepath)
        hash_filepath = os.path.join(cachepath, DEFAULT_HASH_FILE)

    if os.path.exists(cache_filepath):
        if not overwrite:
            raise FileExistsError("Build output file already exists")

        if incremental and not check(
            cache_filepath, hash_filepath=hash_filepath, verbose=verbose
        ):
            return False

        cache = (
            DataFrame(read_csv(cache_filepath, dtype=str))
            if incremental
            else DataFrame()
        )
    else:
        cache = DataFrame()

    for file in files:
        if verbose:
            print("Building from {0}".format(file))

        data = DataFrame(read_csv(file, dtype=str))
        # Reorder data columns to match the cache.
        if len(cache.columns) > 0:
            data = data.reindex(columns=cache.columns)

        if verbose:
            data_shape: Tuple[int, int] = data.shape
            cache_pre_shape: Tuple[int, int] = cache.shape

        cache = cache.append(data)

        if verbose:
            print(
                "Building data {0} onto cache {1} => {2}".format(
                    data_shape, cache_pre_shape, cache.shape
                )
            )

        cache.reset_index(drop=True, inplace=True)

    cache.to_csv(cache_filepath, index=False)

    if post_hash:
        if not os.path.exists(hash_filepath):
            Path(hash_filepath).touch()
        new_entry = HashEntry(cache_filepath)

        with HashFile(hash_filepath) as hashfile:
            hashfile.update(new_entry)

    if verbose:
        print("Built {0}".format(cache_filepath))

    return True
