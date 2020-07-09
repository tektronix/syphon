"""tests.hash.test_hashfile.py

   Copyright Keithley Instruments, LLC.
   Licensed under MIT (https://github.com/tektronix/syphon/blob/master/LICENSE)

"""
from typing import Optional

import pytest
from py._path.local import LocalPath

import syphon.hash

from .. import rand_string


def test_hashfile_init(data_file: str, hash_type: Optional[str]):
    hashfile = syphon.hash.HashFile(data_file, hash_type=hash_type)
    assert hashfile._count == 0
    assert hashfile._file is None
    assert hashfile._hash_type == (
        syphon.hash.DEFAULT_HASH_TYPE if hash_type is None else hash_type
    )
    assert hashfile._original_filepath == data_file
    hashfile.filepath.write_text("")  # Touch the filepath so samefile will work.
    assert hashfile.filepath.samefile(data_file)


def test_hashfile_init_raises_valueerror():
    with pytest.raises(ValueError):
        syphon.hash.HashFile("data file", hash_type=rand_string())


def test_hashfile_is_a_context_manager(hash_file: LocalPath):
    hash_file.write(rand_string())

    hashfile = syphon.hash.HashFile(hash_file)
    assert hashfile._count == 0
    assert hashfile._file is None

    with hashfile as _:
        assert hashfile._count == 1
        assert isinstance(hashfile._file, syphon.hash._OpenHashFile)
        assert hashfile._file._file_obj.readable()
        assert hashfile._file._file_obj.writable()

    assert hashfile._count == 0
    assert hashfile._file is None


def test_hashfile_context_reuses_opened_file(hash_file: LocalPath):
    hash_file.write(rand_string())

    hashfile = syphon.hash.HashFile(hash_file)
    assert hashfile._count == 0
    assert hashfile._file is None

    with hashfile as context1:
        assert hashfile._count == 1
        assert hashfile._file is not None

        with hashfile as context2:
            assert hashfile._count == 2
            assert context1._file_obj.fileno() == context2._file_obj.fileno()

        assert hashfile._count == 1
        assert hashfile._file is not None

    assert hashfile._count == 0
    assert hashfile._file is None


def test_hashfile_context_does_not_suppress_errors():
    with pytest.raises(OSError):
        with syphon.hash.HashFile(rand_string()):
            pass
