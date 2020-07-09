"""tests.assert_utils.py

   Copyright Keithley Instruments, LLC.
   Licensed under MIT (https://github.com/tektronix/syphon/blob/master/LICENSE)

"""
import os
from typing import List, Optional

from _pytest.capture import CaptureResult
from py._path.local import LocalPath


def assert_captured_outerr(captured: CaptureResult, has_stdout: bool, has_stderr: bool):
    if has_stdout:
        assert len(captured.out) > 0, "Expected data on stdout, but found nothing."
    else:
        assert len(captured.out) == 0, f'Unexpected data on stdout: "{captured.out}"'

    if has_stderr:
        assert len(captured.err) > 0, "Expected data on stderr, but found nothing."
    else:
        assert len(captured.err) == 0, f'Unexpected data on stderr: "{captured.err}"'


def assert_matches_outerr(
    captured: CaptureResult, match_out: List[str], match_err: List[str]
):
    for out in match_out:
        assert (
            str(captured.out).find(out) != -1
        ), f'Cannot find "{out}" in "{captured.out}" from stdout'

    for err in match_err:
        assert (
            str(captured.err).find(err) != -1
        ), f'Cannot find "{err}" in "{captured.err}" from stderr'


def assert_post_hash(
    post_hash: bool,
    cache_file: LocalPath,
    hash_filepath: Optional[LocalPath],
    verbose: bool = False,
):
    import syphon.core.check

    resolved_hashfile = (
        cache_file.dirpath(syphon.core.check.DEFAULT_FILE)
        if hash_filepath is None
        else hash_filepath
    )
    if post_hash:
        assert syphon.core.check.check(
            cache_file, hash_filepath=resolved_hashfile, verbose=verbose
        )
    else:
        assert not os.path.exists(resolved_hashfile)
