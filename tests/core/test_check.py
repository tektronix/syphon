"""tests.core.test_check.py

   Copyright Keithley Instruments, LLC.
   Licensed under MIT (https://github.com/tektronix/syphon/blob/master/LICENSE)

"""
import os
import random
from glob import glob
from typing import Iterator, List, Optional, Set

import pytest
from _pytest.capture import CaptureFixture, CaptureResult
from _pytest.monkeypatch import MonkeyPatch
from py._path.local import LocalPath

import syphon.core.check
import syphon.hash

from .. import rand_string, randomize
from ..assert_utils import assert_captured_outerr, assert_matches_outerr


class HashFileOSError(syphon.hash.HashFile):
    def __enter__(self, *args, **kwargs):
        raise OSError()


def make_cache(
    dir: LocalPath, n: int = 1, name_formatter: Optional[str] = None
) -> Iterator[LocalPath]:
    if name_formatter is None:
        name_formatter = "cache%d.csv"

    for i in range(n):
        cache: LocalPath = dir.join(name_formatter % i)
        cache.write(rand_string())
        yield cache


def make_random_file(dir: LocalPath, n) -> Iterator[LocalPath]:
    for i in range(n):
        file: LocalPath = dir.join(rand_string())
        file.write(rand_string())
        yield file


def make_hash_entries(
    tmpdir: LocalPath,
    entries: int,
    irrelevant_entries: int,
    hashfilepath: Optional[LocalPath],
) -> LocalPath:
    """(Also makes cache files in the same directory.)"""
    hashfilepath = resolve_hash(tmpdir, hashfilepath)

    hash_content_list = []
    for cache_file in make_cache(hashfilepath.dirpath(), n=entries):
        hash_content_list.append(str(syphon.hash.HashEntry(cache_file)))

    for random_file in make_random_file(hashfilepath.dirpath(), irrelevant_entries):
        hash_content_list.append(str(syphon.hash.HashEntry(random_file)))

    if len(hash_content_list) > 0:
        hashfilepath.write("\n".join(randomize(*hash_content_list)))

    return hashfilepath


def resolve_hash(tmpdir: LocalPath, hashfile: Optional[LocalPath]) -> LocalPath:
    if hashfile is None:
        return tmpdir.join(syphon.core.check.DEFAULT_FILE)
    return hashfile


@pytest.mark.parametrize("relevant", [i for i in range(1, 4)])
@pytest.mark.parametrize("irrelevant", [j for j in range(0, 4)])
def test_check_true(
    capsys: CaptureFixture,
    tmpdir: LocalPath,
    relevant: int,
    irrelevant: int,
    hash_file: Optional[LocalPath],
    verbose: bool,
):
    # Generate cache files and their respective hash entries.
    new_hashfile: LocalPath = make_hash_entries(tmpdir, relevant, irrelevant, hash_file)
    assert new_hashfile.size() > 0

    # Collect all generated cache files.
    cache_files = glob(str(new_hashfile.dirpath("*.csv")))
    assert len(cache_files) == relevant

    for cache in cache_files:
        assert syphon.check(cache, hash_filepath=hash_file, verbose=verbose)
        captured: CaptureResult = capsys.readouterr()
        assert_captured_outerr(captured, verbose, False)
        if verbose:
            assert_matches_outerr(captured, ["OK"], [])


# Failures must be >0 and <=relevant.
@pytest.mark.parametrize(
    "relevant,failures", [(1, 1), (2, 1), (2, 2), (3, 1), (3, 2), (3, 3)]
)
@pytest.mark.parametrize("irrelevant", [j for j in range(0, 4)])
def test_check_false(
    capsys: CaptureFixture,
    tmpdir: LocalPath,
    relevant: int,
    failures: int,
    irrelevant: int,
    hash_file: Optional[LocalPath],
    verbose: bool,
):
    # Generate cache files and their respective hash entries.
    new_hashfile: LocalPath = make_hash_entries(tmpdir, relevant, irrelevant, hash_file)
    assert new_hashfile.size() > 0

    # Collect all generated cache files.
    cache_files: List[str] = glob(str(new_hashfile.dirpath("*.csv")))
    assert len(cache_files) == relevant

    # Randomly choose files to edit until we've changed the desired number of files.
    edited: Set[str] = set()
    while len(edited) != failures:
        # Choose from the set of files that have not been edited.
        chosen_file = random.choice(list(set(cache_files).difference(edited)))
        assert chosen_file not in edited
        LocalPath(chosen_file).write(rand_string())
        edited.add(chosen_file)

    for cache in cache_files:
        if cache in edited:
            assert not syphon.check(cache, hash_filepath=hash_file, verbose=verbose)
        else:
            assert syphon.check(cache, hash_filepath=hash_file, verbose=verbose)
        captured: CaptureResult = capsys.readouterr()
        assert_captured_outerr(captured, verbose, False)
        if verbose:
            assert_matches_outerr(
                captured, ["FAILED"] if cache in edited else ["OK"], []
            )


def test_check_false_malformedlineerror(
    capsys: CaptureFixture, tmpdir: LocalPath, verbose: bool
):
    # Make a hash entry and cache file.
    new_hashfile: LocalPath = make_hash_entries(tmpdir, 3, 0, None)
    assert new_hashfile.size() > 0

    # Collect all generated cache files.
    cache_files: List[str] = glob(str(new_hashfile.dirpath("*.csv")))
    assert len(cache_files) > 0

    cache: str
    # Identify the hash entry that appears first
    with open(new_hashfile, "rt") as hf:
        first_entry: str = hf.readline()
        for f in cache_files:
            if first_entry.find(os.path.basename(f)) != -1:
                cache = f

    cache_hash = syphon.hash.HashEntry(cache).hash
    for _ in cache_files:
        # The same entry should always be reported.
        assert not syphon.check(
            cache, hash_line_split=lambda line: None, verbose=verbose
        )
        captured: CaptureResult = capsys.readouterr()
        assert_captured_outerr(captured, verbose, False)
        if verbose:
            assert_matches_outerr(captured, [cache_hash, cache], [])


def test_check_false_no_hash_file(
    capsys: CaptureFixture, tmpdir: LocalPath, verbose: bool
):
    # Make a file that we can attempt to check.
    cache_file: LocalPath = [c for c in make_cache(tmpdir)][0]
    assert os.path.exists(cache_file)

    # The default hash file should not exist.
    assert not os.path.exists(resolve_hash(tmpdir, None))

    assert not syphon.check(cache_file, verbose=verbose)
    captured: CaptureResult = capsys.readouterr()
    assert_captured_outerr(captured, verbose, False)
    if verbose:
        assert_matches_outerr(captured, [syphon.core.check.DEFAULT_FILE], [])


def test_check_false_no_file_entry(
    capsys: CaptureFixture, tmpdir: LocalPath, verbose: bool
):
    # Make a hash entry and cache file.
    new_hashfile: LocalPath = make_hash_entries(tmpdir, 1, 0, None)
    assert new_hashfile.size() > 0

    # Try to check a random file.
    random_file: LocalPath = tmpdir.join(rand_string())
    assert not syphon.check(random_file, verbose=verbose)
    captured: CaptureResult = capsys.readouterr()
    assert_captured_outerr(captured, verbose, False)
    if verbose:
        assert_matches_outerr(
            captured, [str(random_file), os.path.basename(new_hashfile)], []
        )


def test_check_false_oserror_cache_file(
    capsys: CaptureFixture, tmpdir: LocalPath, verbose: bool
):
    # Make a hash entry and cache file.
    new_hashfile: LocalPath = make_hash_entries(tmpdir, 1, 0, None)
    assert new_hashfile.size() > 0

    # Collect all generated cache files.
    cache_files = glob(str(new_hashfile.dirpath("*.csv")))
    assert len(cache_files) > 0

    for cache in cache_files:
        # Delete the cache file.
        os.remove(cache)
        # Try to check the cache file.
        assert not syphon.check(cache, verbose=verbose)
        captured: CaptureResult = capsys.readouterr()
        assert_captured_outerr(captured, verbose, False)
        if verbose:
            assert_matches_outerr(captured, [cache], [])


def test_check_false_oserror_hash_file(
    capsys: CaptureFixture, monkeypatch: MonkeyPatch, tmpdir: LocalPath, verbose: bool
):
    with monkeypatch.context() as m:
        # Update the HashFile import to always raise an OSError.
        m.setattr(syphon.core.check, "HashFile", value=HashFileOSError)

        # Generate cache files and their respective hash entries.
        new_hashfile: LocalPath = make_hash_entries(tmpdir, 1, 0, None)
        assert new_hashfile.size() > 0

        # Collect all generated cache files.
        cache_files = glob(str(new_hashfile.dirpath("*.csv")))
        assert len(cache_files) >= 0

        for cache in cache_files:
            # Try to check the cache file.
            assert not syphon.check(cache, verbose=verbose)
            captured: CaptureResult = capsys.readouterr()
            assert_captured_outerr(captured, verbose, False)
            if verbose:
                assert_matches_outerr(captured, [str(new_hashfile)], [])
