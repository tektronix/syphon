"""syphon.core.build.py

   Copyright Keithley Instruments, LLC.
   Licensed under MIT (https://github.com/tektronix/syphon/blob/master/LICENSE)

"""
import os.path
import pathlib
from typing import Optional, Tuple

import pandas as pd

import syphon.core.check
import syphon.hash

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
        cache_filepath: Path to the target output file.
        *files: CSV files to combine.
        hash_filepath: Path to a file containing a SHA256 sum of the cache. If not
            given, then the default is calculated by joining the cache directory with
            `syphon.core.check.DEFAULT_FILE`.
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

    if len(files) == 0:
        if verbose:
            print("Nothing to build")
        return False

    cache_path = pathlib.Path(cache_filepath)

    hash_filepath = (
        os.path.join(cache_path.parents[0], syphon.core.check.DEFAULT_FILE)
        if hash_filepath is None
        else hash_filepath
    )

    if cache_path.exists():
        if not cache_path.is_file():
            raise ValueError(f"Build output is not a file @ {cache_path}")

        if not overwrite:
            raise FileExistsError(f"Build output already exists @ {cache_path}")

        if incremental and not syphon.core.check.check(
            cache_filepath, hash_filepath=hash_filepath, verbose=verbose
        ):
            # NOTE: the check function handles printing status, if necessary.
            return False

        cache = (
            pd.DataFrame(pd.read_csv(cache_path, dtype=str))
            if incremental
            else pd.DataFrame()
        )
    else:
        cache = pd.DataFrame()

    for file in files:
        if verbose:
            print(f"Building from {file}")

        data = pd.DataFrame(pd.read_csv(file, dtype=str))

        if verbose:
            data_shape: Tuple[int, int] = data.shape
            cache_pre_shape: Tuple[int, int] = cache.shape

        cache = cache.append(data)

        if verbose:
            print(
                f"Building data {data_shape} onto cache "
                + f"{cache_pre_shape} => {cache.shape}"
            )

        cache.reset_index(drop=True, inplace=True)

    cache.to_csv(cache_filepath, index=False)

    hash_path = pathlib.Path(hash_filepath)
    if post_hash:
        if not hash_path.exists():
            hash_path.touch()
        new_entry = syphon.hash.HashEntry(cache_filepath)

        with syphon.hash.HashFile(hash_filepath) as hashfile:
            hashfile.update(new_entry)

    if verbose:
        print(f"Built {cache_filepath}")

    return True
