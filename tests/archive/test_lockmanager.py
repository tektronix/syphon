"""syphon.tests.archive.test_lockmanager.py

   Copyright Keithley Instruments, LLC.
   Licensed under MIT (https://github.com/tektronix/syphon/blob/master/LICENSE)

"""
from os.path import exists, join
from time import sleep
from typing import List

import pytest
from py._path.local import LocalPath
from sortedcontainers import SortedList

from syphon.archive._lockmanager import LockManager

MAX_UNIQUE_LOCKS = 5


def test_lockmanager_list_default():
    assert isinstance(LockManager().locks, list)
    assert len(LockManager().locks) == 0


def test_lockmanager_filename_default():
    assert isinstance(LockManager().filename, str)
    assert LockManager().filename is LockManager()._filename


@pytest.mark.parametrize("nlocks", [x for x in range(1, MAX_UNIQUE_LOCKS + 1)])
def test_lockmanager_lock(nlocks: int, tmpdir: LocalPath):
    lockman = LockManager()
    dir_template = "dir{}"

    expected_list = SortedList()

    for n in range(nlocks):
        try:
            path = tmpdir.mkdir(dir_template.format(n))
            lockman.lock(str(path))
        except OSError:
            raise
        else:
            expected_list.add(join(str(path), lockman.filename))

    actual_list = SortedList(lockman.locks)

    assert expected_list == actual_list

    for e in expected_list:
        assert exists(e)


def test_lockmanager_lock_returns_lockfile(tmpdir: LocalPath):
    lockman = LockManager()

    try:
        actual_file: str = lockman.lock(str(tmpdir))
    except OSError:
        raise
    else:
        expected_file: LocalPath = tmpdir.join(lockman.filename)

    assert str(expected_file) == actual_file


@pytest.mark.parametrize("nlocks", [x for x in range(1, MAX_UNIQUE_LOCKS + 1)])
def test_lockmanager_release(nlocks: int, tmpdir: LocalPath):
    lockman = LockManager()
    dir_template = "dir{}"

    lock_list: List[str] = []

    for n in range(nlocks):
        try:
            path: LocalPath = tmpdir.mkdir(dir_template.format(n))
            lockman.lock(str(path))
        except OSError:
            raise
        else:
            lock_list.append(join(str(path), lockman.filename))

    while len(lock_list) != 0:
        lockfile: str = lock_list.pop()
        assert lockfile in lockman.locks
        try:
            lockman.release(lockfile)
        except OSError:
            raise
        else:
            assert lockfile not in lockman.locks

    assert len(lockman.locks) == 0


def test_lockmanager_release_suppress_filenotfounderror(tmpdir: LocalPath):
    lockman = LockManager()

    try:
        lockman.lock(str(tmpdir))
    except OSError:
        raise
    else:
        lockfile: LocalPath = tmpdir.join(lockman.filename)

    try:
        lockfile.remove()
    except OSError:
        raise

    try:
        lockman.release(str(lockfile))
    except FileNotFoundError:
        pytest.fail("LockManager.release raised a FileNotFoundError.")
    except OSError:
        raise
    else:
        assert len(lockman.locks) == 0


@pytest.mark.parametrize("nlocks", [x for x in range(1, MAX_UNIQUE_LOCKS + 1)])
def test_lockmanager_release_all(nlocks: int, tmpdir: LocalPath):
    lockman = LockManager()
    dir_template = "dir{}"

    lock_list: List[str] = []

    for n in range(nlocks):
        try:
            path: LocalPath = tmpdir.mkdir(dir_template.format(n))
            lockman.lock(str(path))
        except OSError:
            raise
        else:
            lock_list.append(join(str(path), lockman.filename))

    try:
        lockman.release_all()
    except OSError:
        raise
    else:
        assert len(lockman.locks) == 0

    for l in lock_list:
        assert not exists(l)


@pytest.mark.parametrize("nlocks", [x for x in range(1, MAX_UNIQUE_LOCKS + 1)])
def test_lockmanager_release_all_suppress_filenotfounderror(
    nlocks: int, tmpdir: LocalPath
):
    lockman = LockManager()
    dir_template = "dir{}"

    for n in range(nlocks):
        try:
            path: LocalPath = tmpdir.mkdir(dir_template.format(n))
            lockman.lock(str(path))
        except OSError:
            raise

        try:
            path.join(lockman.filename).remove()
        except OSError:
            raise

    try:
        lockman.release_all()
    except FileNotFoundError:
        pytest.fail("LockManager.release_all raised a FileNotFoundError.")
    except OSError:
        raise
    else:
        assert len(lockman.locks) == 0


def test_lockmanager_modifiedtime_updated(tmpdir: LocalPath):
    lockman = LockManager()

    try:
        lockman.lock(str(tmpdir))
    except OSError:
        raise
    else:
        lockfile: LocalPath = tmpdir.join(lockman.filename)

    assert exists(str(lockfile))

    # Don't bother specifying the exact type returned.
    # Since `LocalPath.mtime()` wraps `os.stat_result.st_mtime`,
    # the exact return type type may be OS dependant.
    pre_time = lockfile.mtime()
    sleep(1)
    try:
        lockman.lock(str(tmpdir))
    except OSError:
        raise
    else:
        post_time = lockfile.mtime()

    assert pre_time < post_time
