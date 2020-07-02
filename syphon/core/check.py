"""syphon.core.check.py

   Copyright Keithley Instruments, LLC.
   Licensed under MIT (https://github.com/tektronix/syphon/blob/master/LICENSE)

"""
import os.path
import pathlib
from typing import Callable, Optional

import syphon.errors
import syphon.hash

DEFAULT_FILE = ".sha256sums"


def check(
    cache_filepath: str,
    hash_filepath: Optional[str] = None,
    hash_line_split: Optional[
        Callable[[str], Optional[syphon.hash.SplitResult]]
    ] = None,
    verbose: bool = False,
) -> bool:
    # NOTE:
    # the archive & build function use the exact same wording for "hash_filepath".
    """Verify the integrity of the built cache file.

    Args:
        cache_filepath: Path to the target output file.
        hash_filepath: Path to a file containing a SHA256 sum of the cache. If not
            given, then the default is calculated by joining the cache directory with
            `syphon.core.check.DEFAULT_FILE`.
        hash_line_split: A callable object that returns a `syphon.hash.SplitResult`
            from a given line or None if the line is in an unexpected format. Returning
            None raises a MalformedLineError.
        verbose: Whether to print what is being done to the standard output.

    Returns:
        True if the cache file passed the integrity check, False otherwise.
    """

    def _print(message: str) -> None:
        if verbose:
            print(message)

    actual_entry = syphon.hash.HashEntry(cache_filepath)
    if not actual_entry.filepath.exists():
        _print(f"No file exists @ {actual_entry.filepath}")
        return False

    hash_filepath = (
        os.path.join(actual_entry.filepath.parents[0], DEFAULT_FILE)
        if hash_filepath is None
        else hash_filepath
    )
    hash_path = pathlib.Path(hash_filepath)
    if not hash_path.exists():
        _print(f"No file exists @ {hash_filepath}")
        return False

    expected_entry: Optional[syphon.hash.HashEntry] = None
    try:
        # Find the hash entry for the provided cache filepath.
        with syphon.hash.HashFile(hash_filepath) as hashfile:
            hashfile.line_split = hash_line_split
            entry: syphon.hash.HashEntry
            for entry in hashfile:
                if not entry.filepath.exists():
                    continue
                if actual_entry.filepath.samefile(entry.filepath):
                    expected_entry = entry
                    break
    except OSError:
        _print(f"Error reading hash file @ {hash_path.absolute()}")
        return False
    except syphon.errors.MalformedLineError as err:
        _print(f'Error parsing hash entry "{err.line}"')
        return False

    if expected_entry is None:
        _print(f'No entry for file "{cache_filepath}" found in "{hash_path}"')
        return False

    try:
        # The expected entry's hash will already be cached as a side-effect of reading
        # it from the hashfile. That leaves the actual entry to blame for any OSErrors.
        result: bool = expected_entry.hash == actual_entry.hash
        _print(f"{cache_filepath}: {'OK' if result else 'FAILED'}")
        return result
    except OSError:
        _print(f"Error reading cache file @ {cache_filepath}")
        return False
