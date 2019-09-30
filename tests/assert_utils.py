"""tests.assert_utils.py

   Copyright Keithley Instruments, LLC.
   Licensed under MIT (https://github.com/tektronix/syphon/blob/master/LICENSE)

"""
import os
from typing import List, Optional

from _pytest.capture import CaptureResult
from py._path.local import LocalPath


def assert_captured_outerr(captured: CaptureResult, has_stdout: bool, has_stderr: bool):
    no_data_msg = "Expected data on {0}, but found nothing."
    data_msg = 'Unexpected data on {0}: "{1}"'

    if has_stdout:
        assert len(captured.out) > 0, no_data_msg.format("stdout")
    else:
        assert len(captured.out) == 0, data_msg.format("stdout", captured.out)

    if has_stderr:
        assert len(captured.err) > 0, no_data_msg.format("stderr")
    else:
        assert len(captured.err) == 0, data_msg.format("stderr", captured.err)


def assert_matches_outerr(
    captured: CaptureResult, match_out: List[str], match_err: List[str]
):
    match_msg = 'Cannot find "{0}" in "{1}" from {2}'

    for out in match_out:
        assert str(captured.out).find(out) != -1, match_msg.format(
            out, captured.out, "stdout"
        )

    for err in match_err:
        assert str(captured.err).find(err) != -1, match_msg.format(
            err, captured.err, "stderr"
        )


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
