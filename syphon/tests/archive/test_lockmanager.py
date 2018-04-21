"""syphon.tests.archive.test_lockmanager.py

   Copyright (c) 2017-2018 Keithley Instruments, LLC.
   Licensed under MIT (https://github.com/ehall/syphon/blob/master/LICENSE)

"""
from time import sleep
from os.path import isfile, join

import pytest
from sortedcontainers import SortedList
from syphon.archive._lockmanager import LockManager

MAX_UNIQUE_LOCKS = 5


def test_lockmanager_list_default():
    assert isinstance(LockManager().locks, list)
    assert len(LockManager().locks) is 0


def test_lockmanager_filename_default():
    assert isinstance(LockManager().filename, str)
    assert LockManager().filename is LockManager()._filename


@pytest.mark.parametrize('nlocks', [x for x in range(1, MAX_UNIQUE_LOCKS+1)])
def test_lockmanager_lock(nlocks, tmpdir):
    lockman = LockManager()
    dir_template = 'dir{}'

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
        assert isfile(e)


def test_lockmanager_lock_returns_lockfile(tmpdir):
    lockman = LockManager()

    try:
        actual_file = lockman.lock(str(tmpdir))
    except OSError:
        raise
    else:
        expected_file = tmpdir.join(lockman.filename)

    assert str(expected_file) == actual_file


@pytest.mark.parametrize('nlocks', [x for x in range(1, MAX_UNIQUE_LOCKS+1)])
def test_lockmanager_release(nlocks, tmpdir):
    lockman = LockManager()
    dir_template = 'dir{}'

    lock_list = []

    for n in range(nlocks):
        try:
            path = tmpdir.mkdir(dir_template.format(n))
            lockman.lock(str(path))
        except OSError:
            raise
        else:
            lock_list.append(join(str(path), lockman.filename))

    while len(lock_list) is not 0:
        lockfile = lock_list.pop()
        assert lockfile in lockman.locks
        try:
            lockman.release(lockfile)
        except OSError:
            raise
        else:
            assert lockfile not in lockman.locks

    assert len(lockman.locks) is 0


def test_lockmanager_release_suppress_filenotfounderror(tmpdir):
    lockman = LockManager()

    try:
        lockman.lock(str(tmpdir))
    except OSError:
        raise
    else:
        lockfile = tmpdir.join(lockman.filename)

    try:
        lockfile.remove()
    except OSError:
        raise

    try:
        lockman.release(str(lockfile))
    except FileNotFoundError:
        pytest.fail('LockManager.release raised a FileNotFoundError.')
    except OSError:
        raise
    else:
        assert len(lockman.locks) is 0


@pytest.mark.parametrize('nlocks', [x for x in range(1, MAX_UNIQUE_LOCKS+1)])
def test_lockmanager_release_all(nlocks, tmpdir):
    lockman = LockManager()
    dir_template = 'dir{}'

    lock_list = []

    for n in range(nlocks):
        try:
            path = tmpdir.mkdir(dir_template.format(n))
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
        assert len(lockman.locks) is 0

    for l in lock_list:
        assert not isfile(l)


@pytest.mark.parametrize('nlocks', [x for x in range(1, MAX_UNIQUE_LOCKS+1)])
def test_lockmanager_release_all_suppress_filenotfounderror(nlocks, tmpdir):
    lockman = LockManager()
    dir_template = 'dir{}'

    for n in range(nlocks):
        try:
            path = tmpdir.mkdir(dir_template.format(n))
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
        pytest.fail('LockManager.release_all raised a FileNotFoundError.')
    except OSError:
        raise
    else:
        assert len(lockman.locks) is 0


def test_lockmanager_modifiedtime_updated(tmpdir):
    lockman = LockManager()

    try:
        lockman.lock(str(tmpdir))
    except OSError:
        raise
    else:
        lockfile = tmpdir.join(lockman.filename)

    assert isfile(str(lockfile))

    pre_time = lockfile.mtime()
    sleep(1)
    try:
        lockman.lock(str(tmpdir))
    except OSError:
        raise
    else:
        post_time = lockfile.mtime()

    assert pre_time < post_time
