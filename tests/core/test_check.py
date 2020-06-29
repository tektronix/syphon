"""tests.core.test_check.py

   Copyright Keithley Instruments, LLC.
   Licensed under MIT (https://github.com/tektronix/syphon/blob/master/LICENSE)

"""
import os
import random
from glob import glob
from typing import Iterator, List, Optional, Set, Union

import pytest
from _pytest.capture import CaptureFixture, CaptureResult
from _pytest.fixtures import FixtureRequest
from _pytest.monkeypatch import MonkeyPatch
from py._path.local import LocalPath

import syphon.core.check
import syphon.hash

from .. import rand_string, randomize
from ..assert_utils import assert_captured_outerr, assert_matches_outerr
from ..types import PathType


class HashEntryOSError(syphon.hash.HashEntry):
    def _hash(self) -> str:
        raise OSError()


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
        file.write(rand_string())  # Automatically closed.
        yield file


def make_hash_entries(
    tmpdir: LocalPath,
    entries: int,
    irrelevant_entries: int,
    nonexistant_entries: int,
    hashfilepath: Optional[LocalPath],
) -> LocalPath:
    """(Also makes cache files in the same directory.)"""
    hashfilepath = (
        tmpdir.join(syphon.core.check.DEFAULT_FILE)
        if hashfilepath is None
        else hashfilepath
    )

    hash_content_list = []

    cache_file: LocalPath
    for cache_file in make_cache(hashfilepath.dirpath(), n=entries):
        hash_content_list.append(str(syphon.hash.HashEntry(cache_file)))

    random_file: LocalPath
    for random_file in make_random_file(hashfilepath.dirpath(), irrelevant_entries):
        hash_content_list.append(str(syphon.hash.HashEntry(random_file)))

    nonexistant_file: LocalPath
    for nonexistant_file in make_random_file(
        hashfilepath.dirpath(), nonexistant_entries
    ):
        hash_content_list.append(str(syphon.hash.HashEntry(nonexistant_file)))
        nonexistant_file.remove()

    # Randomize the order of the generated hash file entries.
    if len(hash_content_list) > 0:
        hashfilepath.write("\n".join(randomize(*hash_content_list)))

    return hashfilepath


@pytest.mark.parametrize("relevant", [i for i in range(1, 4)])
@pytest.mark.parametrize("irrelevant", [j for j in range(0, 4)])
@pytest.mark.parametrize("nonexistant", [k for k in range(0, 2)])
def test_check_true(
    capsys: CaptureFixture,
    tmpdir: LocalPath,
    relevant: int,
    irrelevant: int,
    nonexistant: int,
    hash_file: Optional[LocalPath],
    verbose: bool,
):
    # Generate cache files and their respective hash entries.
    new_hashfile: LocalPath = make_hash_entries(
        tmpdir, relevant, irrelevant, nonexistant, hash_file
    )
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


class TestPathResolution(object):
    class FS(object):
        def __init__(self, root: LocalPath):
            self.prev_dir: str

            # Make directories.
            self.root = root
            self.level1: LocalPath = self.root.make_numbered_dir(
                prefix="lvl1-dir", rootdir=self.root, keep=3, lock_timeout=300
            )
            self.level2: LocalPath = self.level1.make_numbered_dir(
                prefix="lvl2-dir", rootdir=self.level1, keep=3, lock_timeout=300
            )

            # Resolve filepaths.
            self._cache0: LocalPath = self.root.join("cache0.csv")  # Relative entry
            self._cache1: LocalPath = self.level1.join("cache1.csv")  # Filename entry
            self._cache2: LocalPath = self.level2.join("cache2.csv")  # Absolute entry
            # NOTE: Target-hashfile PathType pairs of the tests below will have to be
            #       reconfigured if the location of the hashfile changes!
            self._hashfile: LocalPath = self.level1.join("sha256sums")

            # Touch files.
            self._cache0.write(rand_string())
            self._cache1.write(rand_string())
            self._cache2.write(rand_string())
            self._hashfile.write("")

        def get_cache0(self, path_type: PathType) -> Union[str, LocalPath]:
            """The hashfile entry for this target is a path RELATIVE to directory
            level1.
            """
            if path_type == PathType.ABSOLUTE:
                return self._cache0
            elif path_type == PathType.RELATIVE:
                return os.path.relpath(self._cache0, os.getcwd())
            else:
                raise TypeError(f"Bad cache0 target PathType '{path_type}'")

        def get_cache1(self, path_type: PathType) -> Union[str, LocalPath]:
            """The hashfile entry for this target is only a filename (PathType.NONE).

            ### SIDE EFFECT WARNING

            Passing `PathType.NONE` will change the current working directory!
            """
            if path_type == PathType.ABSOLUTE:
                return self._cache1
            elif path_type == PathType.RELATIVE:
                return os.path.relpath(self._cache1, os.getcwd())
            elif path_type == PathType.NONE:
                os.chdir(self._cache1.dirpath())  # <-- NOTE side effects!
                return os.path.basename(self._cache1)
            else:
                raise TypeError(f"Bad cache1 target PathType '{path_type}'")

        def get_cache2(self, path_type: PathType) -> Union[str, LocalPath]:
            """The hashfile entry for this target is an ABSOLUTE path.

            ### SIDE EFFECT WARNING

            Passing `PathType.NONE` will change the current working directory!
            """
            if path_type == PathType.ABSOLUTE:
                return self._cache2
            elif path_type == PathType.RELATIVE:
                return os.path.relpath(self._cache2, os.getcwd())
            elif path_type == PathType.NONE:
                os.chdir(self._cache2.dirpath())  # <-- NOTE side effects!
                return os.path.basename(self._cache2)
            else:
                raise TypeError(f"Bad cache2 target PathType '{path_type}'")

        def get_hashfile(self, path_type: PathType) -> Union[str, LocalPath]:
            """
            ### SIDE EFFECT WARNING

            Passing `PathType.NONE` will change the current working directory!
            """
            if path_type == PathType.ABSOLUTE:
                return self._hashfile
            elif path_type == PathType.RELATIVE:
                return os.path.relpath(self._hashfile, os.getcwd())
            elif path_type == PathType.NONE:
                os.chdir(self._hashfile.dirpath())  # <-- NOTE side effects!
                return os.path.basename(self._hashfile)
            else:
                raise TypeError(f"Bad hashfile PathType '{path_type}'")

        def record_hashes(self) -> None:
            entries: List[syphon.hash.HashEntry] = []

            # Relative hash entry.
            # (Relative to directory level1)
            entries.append(
                syphon.hash.HashEntry(os.path.relpath(self._cache0, self.level1))
            )
            # Filename only entry.
            entries.append(syphon.hash.HashEntry(os.path.basename(self._cache1)))
            # Absolute hash entry.
            entries.append(syphon.hash.HashEntry(self._cache2))

            self._hashfile.write("\n".join([str(entry) for entry in entries]))

    @pytest.fixture
    def new_fs(self, tmpdir: LocalPath) -> "TestPathResolution.FS":
        return TestPathResolution.FS(tmpdir)

    @pytest.fixture(scope="function")
    def fs(
        self, request: FixtureRequest, new_fs: "TestPathResolution.FS"
    ) -> "TestPathResolution.FS":
        new_fs.prev_dir = os.getcwd()

        def pop_lvl1():
            os.chdir(new_fs.prev_dir)

        os.chdir(new_fs.level1.realpath())
        new_fs.record_hashes()
        request.addfinalizer(pop_lvl1)

        return new_fs

    @pytest.mark.parametrize(
        "path_type_target,path_type_hashfile",
        [
            (PathType.ABSOLUTE, PathType.ABSOLUTE),
            (PathType.ABSOLUTE, PathType.RELATIVE),
            (PathType.ABSOLUTE, PathType.NONE),
            (PathType.RELATIVE, PathType.ABSOLUTE),
            (PathType.RELATIVE, PathType.RELATIVE),
            (PathType.RELATIVE, PathType.NONE),
        ],
    )
    def test_check_true_target_cache0(
        self,
        capsys: CaptureFixture,
        fs: "TestPathResolution.FS",
        path_type_target: PathType,
        path_type_hashfile: PathType,
        verbose: bool,
    ):
        target: Union[str, LocalPath] = fs.get_cache0(path_type_target)
        # NOTE: Current working directory is changed if PathType.NONE!
        hashfile: Union[str, LocalPath] = fs.get_hashfile(path_type_hashfile)

        # Check cache0.csv using resolved filepaths.
        assert syphon.check(target, hash_filepath=hashfile, verbose=verbose)
        captured: CaptureResult = capsys.readouterr()
        assert_captured_outerr(captured, verbose, False)
        if verbose:
            assert_matches_outerr(captured, ["OK"], [])

    @pytest.mark.parametrize(
        "path_type_target", [PathType.ABSOLUTE, PathType.RELATIVE, PathType.NONE]
    )
    @pytest.mark.parametrize(
        "path_type_hashfile", [PathType.ABSOLUTE, PathType.RELATIVE, PathType.NONE]
    )
    def test_check_true_target_cache1(
        self,
        capsys: CaptureFixture,
        fs: "TestPathResolution.FS",
        path_type_target: PathType,
        path_type_hashfile: PathType,
        verbose: bool,
    ):
        # NOTE: Current working directory is changed if PathType.NONE!
        target: Union[str, LocalPath] = fs.get_cache1(path_type_target)
        # NOTE: Current working directory is changed if PathType.NONE!
        hashfile: Union[str, LocalPath] = fs.get_hashfile(path_type_hashfile)

        # Check cache1.csv using resolved filepaths.
        assert syphon.check(target, hash_filepath=hashfile, verbose=verbose)
        captured: CaptureResult = capsys.readouterr()
        assert_captured_outerr(captured, verbose, False)
        if verbose:
            assert_matches_outerr(captured, ["OK"], [])

    @pytest.mark.parametrize(
        "path_type_target,path_type_hashfile",
        [
            (PathType.ABSOLUTE, PathType.ABSOLUTE),
            (PathType.ABSOLUTE, PathType.RELATIVE),
            (PathType.ABSOLUTE, PathType.NONE),
            (PathType.RELATIVE, PathType.ABSOLUTE),
            (PathType.RELATIVE, PathType.RELATIVE),
            (PathType.RELATIVE, PathType.NONE),
            (PathType.NONE, PathType.ABSOLUTE),
            (PathType.NONE, PathType.RELATIVE),
        ],
    )
    def test_check_true_target_cache2(
        self,
        capsys: CaptureFixture,
        fs: "TestPathResolution.FS",
        path_type_target: PathType,
        path_type_hashfile: PathType,
        verbose: bool,
    ):
        # NOTE: Current working directory is changed if PathType.NONE!
        target: Union[str, LocalPath] = fs.get_cache1(path_type_target)
        # NOTE: Current working directory is changed if PathType.NONE!
        hashfile: Union[str, LocalPath] = fs.get_hashfile(path_type_hashfile)

        # Check cache2.csv using resolved filepaths.
        assert syphon.check(target, hash_filepath=hashfile, verbose=verbose)
        captured: CaptureResult = capsys.readouterr()
        assert_captured_outerr(captured, verbose, False)
        if verbose:
            assert_matches_outerr(captured, ["OK"], [])


# Failures must be >0 and <=relevant.
@pytest.mark.parametrize(
    "relevant,failures", [(1, 1), (2, 1), (2, 2), (3, 1), (3, 2), (3, 3)]
)
@pytest.mark.parametrize("irrelevant", [j for j in range(0, 4)])
@pytest.mark.parametrize("nonexistant", [k for k in range(0, 2)])
def test_check_false(
    capsys: CaptureFixture,
    tmpdir: LocalPath,
    relevant: int,
    failures: int,
    irrelevant: int,
    nonexistant: int,
    hash_file: Optional[LocalPath],
    verbose: bool,
):
    # Generate cache files and their respective hash entries.
    new_hashfile: LocalPath = make_hash_entries(
        tmpdir, relevant, irrelevant, nonexistant, hash_file
    )
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
    new_hashfile: LocalPath = make_hash_entries(tmpdir, 3, 0, 0, None)
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
    assert not os.path.exists(tmpdir.join(syphon.core.check.DEFAULT_FILE))

    assert not syphon.check(cache_file, verbose=verbose)
    captured: CaptureResult = capsys.readouterr()
    assert_captured_outerr(captured, verbose, False)
    if verbose:
        assert_matches_outerr(captured, [syphon.core.check.DEFAULT_FILE], [])


def test_check_false_no_file_entry(
    capsys: CaptureFixture, tmpdir: LocalPath, verbose: bool
):
    # Make a hash entry and cache file.
    new_hashfile: LocalPath = make_hash_entries(tmpdir, 1, 0, 0, None)
    assert new_hashfile.size() > 0

    # Try to check a random file.
    random_file: LocalPath = tmpdir.join(rand_string())
    # Create it to prevent File Does Not Exist errors.
    random_file.write("")
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
    new_hashfile: LocalPath = make_hash_entries(tmpdir, 1, 0, 0, None)
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


def test_check_false_oserror_hashing_cache_file(
    capsys: CaptureFixture, monkeypatch: MonkeyPatch, tmpdir: LocalPath, verbose: bool
):
    # Generate cache files and their respective hash entries before patching.
    new_hashfile: LocalPath = make_hash_entries(tmpdir, 1, 0, 0, None)
    assert new_hashfile.size() > 0

    with monkeypatch.context() as m:
        # Update HashEntry._hash to always raise an OSError.
        m.setattr(syphon.hash, "HashEntry", value=HashEntryOSError)

        # Collect all generated cache files.
        cache_files = glob(str(new_hashfile.dirpath("*.csv")))
        assert len(cache_files) >= 0

        for cache in cache_files:
            # Try to check the cache file.
            assert not syphon.check(cache, verbose=verbose)
            captured: CaptureResult = capsys.readouterr()
            assert_captured_outerr(captured, verbose, False)
            if verbose:
                assert_matches_outerr(captured, [str(cache)], [])


def test_check_false_oserror_hash_file(
    capsys: CaptureFixture, monkeypatch: MonkeyPatch, tmpdir: LocalPath, verbose: bool
):
    with monkeypatch.context() as m:
        # Update HashFile.__enter__ to always raise an OSError.
        m.setattr(syphon.hash, "HashFile", value=HashFileOSError)

        # Generate cache files and their respective hash entries.
        new_hashfile: LocalPath = make_hash_entries(tmpdir, 1, 0, 0, None)
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
