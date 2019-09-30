"""tests.hash.test_openhashfile.py

   Copyright Keithley Instruments, LLC.
   Licensed under MIT (https://github.com/tektronix/syphon/blob/master/LICENSE)

"""
import enum
import os
import random
from typing import List, Optional

import pytest
from _pytest.monkeypatch import MonkeyPatch
from py._path.local import LocalPath

import syphon.hash
from _io import _IOBase

from .. import get_data_path, rand_string, randomize


class CacheEntryPosition(enum.Enum):
    FIRST = 0
    RANDOM = 1
    LAST = 2


def populate_hash_file(
    hash_file: LocalPath,
    cache_file: Optional[LocalPath] = None,
    cache_position: CacheEntryPosition = CacheEntryPosition.RANDOM,
    final_newline: bool = True,
) -> List[syphon.hash.HashEntry]:
    # Generate hashfile content.
    expected_entries: List[syphon.hash.HashEntry] = [
        syphon.hash.HashEntry(os.path.join(get_data_path(), "empty.csv")),
        syphon.hash.HashEntry(os.path.join(get_data_path(), "iris.csv")),
        syphon.hash.HashEntry(os.path.join(get_data_path(), "iris_plus.csv")),
    ]
    expected_entries = randomize(*expected_entries)

    if cache_file is not None:
        if cache_position == CacheEntryPosition.FIRST:
            expected_entries.insert(0, syphon.hash.HashEntry(cache_file))
        elif cache_position == CacheEntryPosition.RANDOM:
            expected_entries.insert(
                random.randint(1, len(expected_entries) - 1),
                syphon.hash.HashEntry(cache_file),
            )
        elif cache_position == CacheEntryPosition.LAST:
            expected_entries.append(syphon.hash.HashEntry(cache_file))

    hashfile_content = "\n".join([str(e) for e in expected_entries])
    # There's a test that checks for proper handling of files without a trailing
    # newline, so we should make our file with the opposite case.
    hash_file.write(hashfile_content + "\n" if final_newline else "")

    return expected_entries


def test_openhashfile_init(hash_file: LocalPath, hash_type: Optional[str]):
    if hash_type is None:
        hash_type = syphon.hash.DEFAULT_HASH_TYPE

    hash_file.write(rand_string())

    file_obj: _IOBase = hash_file.open("r+t")
    openhashfile = syphon.hash._OpenHashFile(file_obj, hash_type)
    try:
        assert file_obj.fileno() == openhashfile._file_obj.fileno()
        assert not openhashfile._file_obj.closed
        assert openhashfile.hash_type == hash_type
        assert openhashfile.line_split is None
    finally:
        file_obj.close()
        openhashfile._file_obj.close()


def test_openhashfile_close(hash_file: LocalPath):
    hash_file.write(rand_string())

    openhashfile = syphon.hash._OpenHashFile(hash_file.open("r+t"), "")

    openhashfile.close()
    try:
        assert openhashfile._file_obj.closed
    finally:
        openhashfile._file_obj.close()


def test_openhashfile_items_are_hashentries(tmpdir: LocalPath):
    target_hashfile: LocalPath = tmpdir.join("sha256sums")

    expected_entries: List[syphon.hash.HashEntry] = populate_hash_file(target_hashfile)

    # Iterate through the hash file entries.
    with syphon.hash.HashFile(target_hashfile) as openfile:
        for actual in openfile:
            expected = expected_entries.pop(0)
            assert isinstance(actual, syphon.hash.HashEntry)
            assert str(expected) == str(actual)


def test_openhashfile_tell(hash_file: LocalPath):
    hash_file.write(rand_string())

    openhashfile = syphon.hash._OpenHashFile(hash_file.open("r+t"), "")
    assert openhashfile.tell() == 0
    assert openhashfile.tell() == openhashfile._file_obj.tell()

    line = openhashfile._file_obj.readline()
    assert openhashfile._file_obj.tell() == len(line)


class TestAppend(object):
    @staticmethod
    def test_adds_to_end(cache_file: LocalPath, hash_file: LocalPath):
        cache_file.write(rand_string())

        populate_hash_file(hash_file)

        expected_final_entry = syphon.hash.HashEntry(cache_file)

        with syphon.hash.HashFile(hash_file) as hashfile:
            hashfile.append(expected_final_entry)

        with syphon.hash.HashFile(hash_file) as hashfile:
            for actual_final_entry in hashfile:
                pass

        assert expected_final_entry.binary == actual_final_entry.binary
        assert expected_final_entry.filepath == actual_final_entry.filepath
        assert expected_final_entry.hash == actual_final_entry.hash
        assert str(expected_final_entry) == str(actual_final_entry)

    @staticmethod
    def test_handles_last_line_lacking_newline(
        cache_file: LocalPath, hash_file: LocalPath
    ):
        cache_file.write(rand_string())

        populate_hash_file(hash_file, final_newline=False)

        expected_final_entry = syphon.hash.HashEntry(cache_file)

        with syphon.hash.HashFile(hash_file) as hashfile:
            hashfile.append(expected_final_entry)

        with syphon.hash.HashFile(hash_file) as hashfile:
            for actual_final_entry in hashfile:
                pass

        assert expected_final_entry.binary == actual_final_entry.binary
        assert expected_final_entry.filepath == actual_final_entry.filepath
        assert expected_final_entry.hash == actual_final_entry.hash
        assert str(expected_final_entry) == str(actual_final_entry)

    @staticmethod
    def test_populates_first_line_when_hashfile_empty(
        cache_file: LocalPath, hash_file: LocalPath
    ):
        cache_file.write(rand_string())

        hash_file.write("")

        expected_final_entry = syphon.hash.HashEntry(cache_file)

        with syphon.hash.HashFile(hash_file) as hashfile:
            hashfile.append(expected_final_entry)

        with syphon.hash.HashFile(hash_file) as hashfile:
            for actual_first_entry in hashfile:
                break

        assert expected_final_entry.binary == actual_first_entry.binary
        assert expected_final_entry.filepath == actual_first_entry.filepath
        assert expected_final_entry.hash == actual_first_entry.hash
        assert str(expected_final_entry) == str(actual_first_entry)

    @staticmethod
    def test_raises_valueerror_on_mismatching_hash_type(
        cache_file: LocalPath, hash_file: LocalPath
    ):
        cache_file.write(rand_string())

        hash_file.write("")

        entry = syphon.hash.HashEntry(cache_file)
        entry.hash_type = "md5"

        with pytest.raises(ValueError, match=entry.hash_type):
            with syphon.hash.HashFile(hash_file) as hashfile:
                hashfile.append(entry)


class TestUpdate(object):
    @staticmethod
    @pytest.mark.parametrize(
        "entry_position",
        [CacheEntryPosition.FIRST, CacheEntryPosition.RANDOM, CacheEntryPosition.LAST],
    )
    @pytest.mark.parametrize("final_newline", [True, False])
    def test_updates_existing_entry(
        cache_file: LocalPath,
        hash_file: LocalPath,
        entry_position: CacheEntryPosition,
        final_newline: bool,
    ):
        cache_file.write(rand_string())

        populate_hash_file(
            hash_file,
            cache_file=cache_file,
            cache_position=entry_position,
            final_newline=final_newline,
        )

        cache_file.write(rand_string())
        expected_entry = syphon.hash.HashEntry(cache_file)

        with syphon.hash.HashFile(hash_file) as hashfile:
            hashfile.update(expected_entry)

        with syphon.hash.HashFile(hash_file) as hashfile:
            for actual_entry in hashfile:
                if expected_entry.filepath == actual_entry.filepath:
                    break

        assert expected_entry.binary == actual_entry.binary
        assert expected_entry.filepath == actual_entry.filepath
        assert expected_entry.hash == actual_entry.hash
        assert str(expected_entry) == str(actual_entry)

    @staticmethod
    def test_appends_when_entry_does_not_exist(
        monkeypatch: MonkeyPatch, cache_file: LocalPath, hash_file: LocalPath
    ):
        def raise_assertionerror(*args, **kwargs):
            raise AssertionError()

        with monkeypatch.context() as m:
            # Throw an AssertionError when append is called.
            m.setattr(syphon.hash._OpenHashFile, "append", value=raise_assertionerror)

            cache_file.write(rand_string())

            populate_hash_file(hash_file)

            entry = syphon.hash.HashEntry(cache_file)

            with pytest.raises(AssertionError):
                with syphon.hash.HashFile(hash_file) as hashfile:
                    hashfile.update(entry)

    @staticmethod
    def test_raises_valueerror_on_mismatching_hash_type(
        cache_file: LocalPath, hash_file: LocalPath
    ):
        cache_file.write(rand_string())

        hash_file.write("")

        entry = syphon.hash.HashEntry(cache_file)
        entry.hash_type = "md5"

        with pytest.raises(ValueError, match=entry.hash_type):
            with syphon.hash.HashFile(hash_file) as hashfile:
                hashfile.update(entry)
