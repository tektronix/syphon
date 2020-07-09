"""tests.hash.test_hashentry.py

   Copyright Keithley Instruments, LLC.
   Licensed under MIT (https://github.com/tektronix/syphon/blob/master/LICENSE)

"""
import hashlib
import os
import pathlib
from typing import List, Optional

import pytest
from py._path.local import LocalPath

from syphon.errors import MalformedLineError
from syphon.hash import DEFAULT_HASH_TYPE, HashEntry, SplitResult

from .. import get_data_path, rand_string
from . import _copy


def test_hashentry_init(data_file: str, binary_hash: bool, hash_type: Optional[str]):
    entry = HashEntry(data_file, binary=binary_hash, hash_type=hash_type)
    assert entry._hash_cache == ""
    assert entry._hash_obj.name == DEFAULT_HASH_TYPE if hash_type is None else hash_type
    assert entry._original_filepath == data_file
    assert entry._raw_entry == ""
    assert entry.binary == binary_hash
    entry.filepath.write_text("")  # Touch the filepath so samefile will work.
    assert entry.filepath.samefile(data_file)


def test_hashentry_init_raises_valueerror():
    bad_hash_type = rand_string()

    with pytest.raises(ValueError, match=bad_hash_type):
        HashEntry("datafile", hash_type=bad_hash_type)


def test_hashentry_str(
    cache_file: LocalPath, data_file: str, binary_hash: bool, hash_type: Optional[str]
):
    target = LocalPath(os.path.join(get_data_path(), data_file))
    _copy(target, cache_file)
    assert os.path.exists(cache_file)

    entry = HashEntry(str(cache_file), binary=binary_hash, hash_type=hash_type)

    expected_str = f"{entry._hash()} {'*' if binary_hash else ' '}{str(cache_file)}"
    # We've fed content to the hash object, so we have to reinitialize it.
    entry._hash_obj = hashlib.new(entry._hash_obj.name)

    assert expected_str == str(entry)


def test_hashentry_cached_after_hash(cache_file: LocalPath, data_file: str):
    target = LocalPath(os.path.join(get_data_path(), data_file))
    _copy(target, cache_file)
    assert os.path.exists(cache_file)

    entry = HashEntry(str(cache_file))
    assert not entry.cached

    _ = entry.hash
    assert entry.cached


def test_hashentry_hash(
    cache_file: LocalPath, data_file: str, hash_type: Optional[str]
):
    target = LocalPath(os.path.join(get_data_path(), data_file))
    _copy(target, cache_file)
    assert os.path.exists(cache_file)

    entry = HashEntry(str(cache_file), hash_type=hash_type)

    if hash_type is None:
        hash_type = DEFAULT_HASH_TYPE
    hash_obj = hashlib.new(hash_type)
    with open(cache_file, "r") as fd:
        hash_obj.update(bytes(fd.read(), fd.encoding))
    expected_hash: str = hash_obj.hexdigest()

    assert expected_hash == entry.hash


def test_hashentry_hash_uses_cache():
    expected_hash = rand_string()

    entry = HashEntry("datafile")
    entry._hash_cache = expected_hash

    assert expected_hash == entry.hash


def test_hashentry_hash_type_getter(hash_type: Optional[str]):
    entry = HashEntry("datafile", hash_type=hash_type)
    assert entry.hash_type == DEFAULT_HASH_TYPE if hash_type is None else hash_type

    assert entry.hash_type == entry._hash_obj.name


def test_hashentry_hash_type_setter(hash_type: Optional[str]):
    if hash_type is None:
        hash_type = DEFAULT_HASH_TYPE

    entry = HashEntry("datafile")
    assert entry.hash_type == DEFAULT_HASH_TYPE

    entry._hash_obj.update(bytes(rand_string(), "utf-8"))
    pre_hash = entry._hash_obj.digest()

    # Assert that the hash object is reinstantiated if the hash type changes.
    entry.hash_type = hash_type
    if hash_type == DEFAULT_HASH_TYPE:
        assert entry._hash_obj.digest() == pre_hash
    else:
        assert entry._hash_obj.digest() != pre_hash


def test_hashentry_hash_type_setter_raises_typeerror():
    entry = HashEntry("datafile")

    entry._hash_obj.update(bytes(rand_string(), "utf-8"))
    pre_hash = entry._hash_obj.digest()
    pre_hash_name = entry.hash_type

    with pytest.raises(TypeError):
        entry.hash_type = 0

    # Assert that the original hash state is retained.
    assert pre_hash == entry._hash_obj.digest()
    assert pre_hash_name == entry.hash_type


def test_hashentry_hash_type_setter_raises_valueerror():
    entry = HashEntry("datafile")

    entry._hash_obj.update(bytes(rand_string(), "utf-8"))
    pre_hash = entry._hash_obj.digest()
    pre_hash_name = entry.hash_type

    with pytest.raises(ValueError):
        entry.hash_type = rand_string()

    # Assert that the original hash state is retained.
    assert pre_hash == entry._hash_obj.digest()
    assert pre_hash_name == entry.hash_type


def test_hashentry_from_str(
    cache_file: LocalPath, data_file: str, binary_hash: bool, hash_type: Optional[str]
):
    target = LocalPath(os.path.join(get_data_path(), data_file))
    _copy(target, cache_file)
    assert os.path.exists(cache_file)

    expected_entry = HashEntry(str(cache_file), binary=binary_hash, hash_type=hash_type)
    actual_entry = HashEntry.from_str(str(expected_entry), hash_type=hash_type)
    assert str(expected_entry) == actual_entry._raw_entry

    assert os.path.samefile(expected_entry.filepath, actual_entry.filepath)
    assert expected_entry.hash == actual_entry.hash


def test_hashentry_from_str_line_split():
    def line_split(line: str) -> SplitResult:
        found: List[str] = line.split(" ")
        return SplitResult(hash=found[0], file=found[1], binary=True)

    entry = HashEntry.from_str("hash datafile", line_split)
    assert entry._hash_cache == "hash"
    assert entry._original_filepath == "datafile"
    assert entry.binary
    assert entry.filepath == pathlib.Path("datafile")


def test_hashentry_from_str_raises_malformedlineerror():
    bad_entry = "this is a malformed entry\n"

    with pytest.raises(MalformedLineError) as err:
        HashEntry.from_str(bad_entry)

    assert bad_entry.strip() == err.value.line
