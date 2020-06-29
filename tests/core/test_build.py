"""tests.core.test_build.py

   Copyright Keithley Instruments, LLC.
   Licensed under MIT (https://github.com/tektronix/syphon/blob/master/LICENSE)

"""
import os
import pathlib
from typing import List, Optional

import pytest
from _pytest.capture import CaptureFixture
from pandas import DataFrame, read_csv
from pandas.testing import assert_frame_equal
from py._path.local import LocalPath
from sortedcontainers import SortedDict

import syphon
import syphon.core.build
import syphon.core.check
import syphon.hash
import syphon.schema

from .. import get_data_path, rand_string
from ..assert_utils import assert_captured_outerr, assert_post_hash


def get_data_files(archive_dir: LocalPath) -> List[str]:
    file_list: List[str] = list()
    for root, _, files in os.walk(str(archive_dir)):
        for file in files:
            # skip linux-style hidden files
            if not file.startswith(syphon.core.build.LINUX_HIDDEN_CHAR):
                file_list.append(os.path.join(root, file))
    return file_list


class TestBuild(object):
    @staticmethod
    def test_does_nothing_when_given_zero_files(
        capsys: CaptureFixture,
        cache_file: LocalPath,
        hash_file: Optional[LocalPath],
        incremental: bool,
        overwrite: bool,
        post_hash: bool,
        verbose: bool,
    ):
        cache_file.write(rand_string())
        expected_cache_hash: str = syphon.hash.HashEntry(cache_file).hash

        assert not syphon.build(
            cache_file,
            *[],
            hash_filepath=hash_file,
            incremental=incremental,
            overwrite=overwrite,
            post_hash=post_hash,
            verbose=verbose,
        )
        assert_post_hash(False, cache_file, hash_filepath=hash_file)
        assert_captured_outerr(capsys.readouterr(), verbose, False)

        actual_cache_hash: str = syphon.hash.HashEntry(cache_file).hash
        assert expected_cache_hash == actual_cache_hash

    @staticmethod
    def test_full_build_with_schema_maintains_data_fidelity(
        capsys: CaptureFixture,
        archive_dir: LocalPath,
        cache_file: LocalPath,
        hash_file: Optional[LocalPath],
        overwrite: bool,
        post_hash: bool,
        verbose: bool,
    ):
        datafile: str = os.path.join(get_data_path(), "iris.csv")
        schema = SortedDict({"0": "Name"})
        schemafile = os.path.join(archive_dir, syphon.schema.DEFAULT_FILE)

        syphon.init(schema, schemafile, overwrite=overwrite)
        assert syphon.archive(
            archive_dir, [datafile], schema_filepath=schemafile, overwrite=overwrite
        )
        assert not os.path.exists(os.path.join(get_data_path(), "#lock"))

        expected_frame = DataFrame(read_csv(datafile, dtype=str, index_col="Index"))
        expected_frame.sort_index(inplace=True)

        if overwrite:
            cache_file.write(rand_string())

        assert syphon.build(
            cache_file,
            *get_data_files(archive_dir),
            hash_filepath=hash_file,
            incremental=False,
            overwrite=overwrite,
            post_hash=post_hash,
            verbose=verbose,
        )
        assert_post_hash(post_hash, cache_file, hash_filepath=hash_file)

        actual_frame = DataFrame(read_csv(cache_file, dtype=str, index_col="Index"))
        actual_frame.sort_index(inplace=True)

        assert_frame_equal(expected_frame, actual_frame, check_exact=True)
        assert_captured_outerr(capsys.readouterr(), verbose, False)

    @staticmethod
    def test_full_build_without_schema_maintains_data_fidelity(
        capsys: CaptureFixture,
        archive_dir: LocalPath,
        cache_file: LocalPath,
        hash_file: Optional[LocalPath],
        overwrite: bool,
        post_hash: bool,
        verbose: bool,
    ):
        datafile: str = os.path.join(get_data_path(), "iris.csv")

        assert syphon.archive(archive_dir, [datafile], overwrite=overwrite)
        assert not os.path.exists(os.path.join(get_data_path(), "#lock"))

        expected_frame = DataFrame(read_csv(datafile, dtype=str, index_col="Index"))
        expected_frame.sort_index(inplace=True)

        if overwrite:
            cache_file.write(rand_string())

        assert syphon.build(
            cache_file,
            *get_data_files(archive_dir),
            hash_filepath=hash_file,
            incremental=False,
            overwrite=overwrite,
            post_hash=post_hash,
            verbose=verbose,
        )
        assert_post_hash(post_hash, cache_file, hash_filepath=hash_file)

        actual_frame = DataFrame(read_csv(cache_file, dtype=str, index_col="Index"))
        actual_frame.sort_index(inplace=True)

        assert_frame_equal(expected_frame, actual_frame, check_exact=True)
        assert_captured_outerr(capsys.readouterr(), verbose, False)

    @staticmethod
    @pytest.mark.parametrize("schema", [True, False])
    def test_incremental_becomes_full_build_when_cache_does_not_exist(
        capsys: CaptureFixture,
        schema: bool,
        archive_dir: LocalPath,
        cache_file: LocalPath,
        hash_file: Optional[LocalPath],
        post_hash: bool,
        verbose: bool,
    ):
        datafile: str = os.path.join(get_data_path(), "iris.csv")
        schema = SortedDict({"0": "Name"})
        schemafile = os.path.join(archive_dir, syphon.schema.DEFAULT_FILE)

        if schema:
            syphon.init(schema, schemafile)
        assert syphon.archive(
            archive_dir, [datafile], schema_filepath=schemafile if schema else None
        )
        assert not os.path.exists(os.path.join(get_data_path(), "#lock"))

        expected_frame = DataFrame(read_csv(datafile, dtype=str, index_col="Index"))
        expected_frame.sort_index(inplace=True)

        # Raises a FileExistsError unless a full build is performed.
        assert syphon.build(
            cache_file,
            *get_data_files(archive_dir),
            hash_filepath=hash_file,
            incremental=True,
            post_hash=post_hash,
            verbose=verbose,
        )
        assert_post_hash(post_hash, cache_file, hash_filepath=hash_file)

        actual_frame = DataFrame(read_csv(cache_file, dtype=str, index_col="Index"))
        actual_frame.sort_index(inplace=True)

        assert_frame_equal(expected_frame, actual_frame, check_exact=True)
        assert_captured_outerr(capsys.readouterr(), verbose, False)

    @staticmethod
    @pytest.mark.parametrize("schema", [True, False])
    def test_incremental_fails_when_check_fails(
        capsys: CaptureFixture,
        schema: bool,
        archive_dir: LocalPath,
        cache_file: LocalPath,
        hash_file: Optional[LocalPath],
        post_hash: bool,
        verbose: bool,
    ):
        datafile: str = os.path.join(get_data_path(), "iris.csv")
        schema = SortedDict({"0": "Name"})
        schemafile = os.path.join(archive_dir, syphon.schema.DEFAULT_FILE)

        if schema:
            syphon.init(schema, schemafile)
        assert syphon.archive(
            archive_dir, [datafile], schema_filepath=schemafile if schema else None
        )
        assert not os.path.exists(os.path.join(get_data_path(), "#lock"))

        expected_frame = DataFrame(read_csv(datafile, dtype=str, index_col="Index"))
        expected_frame.sort_index(inplace=True)

        LocalPath(datafile).copy(cache_file)
        assert os.path.exists(cache_file)

        # "check" ought to fail when the hash file does not exist.
        assert not syphon.check(cache_file, hash_filepath=hash_file)
        # If "check" fails, then the incremental build fails.
        assert not syphon.build(
            cache_file,
            *get_data_files(archive_dir),
            hash_filepath=hash_file,
            incremental=True,
            overwrite=True,
            post_hash=post_hash,
            verbose=verbose,
        )
        assert_post_hash(False, cache_file, hash_filepath=hash_file)

        actual_frame = DataFrame(read_csv(cache_file, dtype=str, index_col="Index"))
        actual_frame.sort_index(inplace=True)

        assert_frame_equal(expected_frame, actual_frame, check_exact=True)
        assert_captured_outerr(capsys.readouterr(), verbose, False)

    @staticmethod
    def test_incremental_maintains_data_fidelity(
        capsys: CaptureFixture,
        archive_dir: LocalPath,
        import_dir: LocalPath,
        cache_file: LocalPath,
        hash_file: Optional[LocalPath],
        verbose: bool,
    ):
        pre_datafiles: List[str] = [
            os.path.join(get_data_path(), "iris-part-1-of-6-combined.csv"),
            os.path.join(get_data_path(), "iris-part-2-of-6-combined.csv"),
            os.path.join(get_data_path(), "iris-part-3-of-6-combined.csv"),
        ]
        datafiles: List[str] = [
            os.path.join(get_data_path(), "iris-part-4-of-6-combined.csv"),
            os.path.join(get_data_path(), "iris-part-5-of-6-combined.csv"),
            os.path.join(get_data_path(), "iris-part-6-of-6-combined.csv"),
        ]

        resolved_hashfile = (
            cache_file.dirpath(syphon.core.check.DEFAULT_FILE)
            if hash_file is None
            else hash_file
        )

        assert syphon.archive(archive_dir, pre_datafiles)
        assert not os.path.exists(os.path.join(get_data_path(), "#lock"))

        # Pre-build
        assert syphon.build(
            cache_file,
            *get_data_files(archive_dir),
            hash_filepath=hash_file,
            incremental=False,
            overwrite=False,
            post_hash=True,
            verbose=False,
        )
        # Get the hash of the cache file before our main build.
        pre_cache_hash: str = syphon.hash.HashEntry(cache_file).hash
        # Get the hash of the hash file for easy file change checking.
        pre_hash_hash: str = syphon.hash.HashEntry(resolved_hashfile).hash

        # Main build
        assert syphon.build(
            cache_file,
            *datafiles,
            hash_filepath=hash_file,
            incremental=True,
            overwrite=True,
            post_hash=True,
            verbose=verbose,
        )
        assert_captured_outerr(capsys.readouterr(), verbose, False)

        post_cache_hash: str = syphon.hash.HashEntry(cache_file).hash
        post_hash_hash: str = syphon.hash.HashEntry(resolved_hashfile).hash

        expected_frame = DataFrame(
            read_csv(
                os.path.join(get_data_path(), "iris_plus.csv"),
                dtype=str,
                index_col="Index",
            )
        )
        expected_frame.sort_index(inplace=True)

        assert pre_cache_hash != post_cache_hash
        assert pre_hash_hash != post_hash_hash

        with syphon.hash.HashFile(resolved_hashfile) as hashfile:
            for entry in hashfile:
                if os.path.samefile(entry.filepath, str(cache_file)):
                    assert post_cache_hash == entry.hash

        actual_frame = DataFrame(read_csv(cache_file, dtype=str, index_col="Index"))
        actual_frame.sort_index(inplace=True)

        assert_frame_equal(expected_frame, actual_frame, check_exact=True)

    @staticmethod
    def test_only_create_hash_file_when_post_hash_true(
        capsys: CaptureFixture,
        archive_dir: LocalPath,
        cache_file: LocalPath,
        hash_file: Optional[LocalPath],
        verbose: bool,
    ):
        datafile: str = os.path.join(get_data_path(), "iris.csv")
        assert syphon.archive(archive_dir, [datafile])
        assert not os.path.exists(os.path.join(get_data_path(), "#lock"))

        resolved_hashfile = (
            cache_file.dirpath(syphon.core.check.DEFAULT_FILE)
            if hash_file is None
            else hash_file
        )

        assert not os.path.exists(resolved_hashfile)
        assert syphon.build(
            cache_file,
            *get_data_files(archive_dir),
            hash_filepath=hash_file,
            incremental=False,
            overwrite=True,
            post_hash=False,
            verbose=verbose,
        )
        assert not os.path.exists(resolved_hashfile)
        assert_captured_outerr(capsys.readouterr(), verbose, False)
        assert syphon.build(
            cache_file,
            *get_data_files(archive_dir),
            hash_filepath=hash_file,
            incremental=False,
            overwrite=True,
            post_hash=True,
            verbose=verbose,
        )
        assert os.path.exists(resolved_hashfile)
        assert_captured_outerr(capsys.readouterr(), verbose, False)

    @staticmethod
    def test_only_update_hash_file_when_post_hash_true(
        capsys: CaptureFixture,
        archive_dir: LocalPath,
        cache_file: LocalPath,
        hash_file: Optional[LocalPath],
        verbose: bool,
    ):
        datafile: str = os.path.join(get_data_path(), "iris.csv")
        assert syphon.archive(archive_dir, [datafile])
        assert not os.path.exists(os.path.join(get_data_path(), "#lock"))

        cache_file.write(rand_string())

        resolved_hashfile = (
            cache_file.dirpath(syphon.core.check.DEFAULT_FILE)
            if hash_file is None
            else hash_file
        )
        pathlib.Path(resolved_hashfile).touch()
        with syphon.hash.HashFile(resolved_hashfile) as hashfile:
            hashfile.update(syphon.hash.HashEntry(cache_file))

        assert syphon.check(cache_file, hash_filepath=resolved_hashfile)
        assert syphon.build(
            cache_file,
            *get_data_files(archive_dir),
            hash_filepath=hash_file,
            incremental=False,
            overwrite=True,
            post_hash=False,
            verbose=verbose,
        )
        assert_captured_outerr(capsys.readouterr(), verbose, False)
        assert not syphon.check(cache_file, hash_filepath=resolved_hashfile)
        assert syphon.build(
            cache_file,
            *get_data_files(archive_dir),
            hash_filepath=hash_file,
            incremental=False,
            overwrite=True,
            post_hash=True,
            verbose=verbose,
        )
        assert_captured_outerr(capsys.readouterr(), verbose, False)
        assert syphon.check(cache_file, hash_filepath=resolved_hashfile)

    @staticmethod
    def test_raises_fileexistserror_when_cache_exists_during_full_build(
        archive_dir: LocalPath, cache_file: LocalPath, hash_file: Optional[LocalPath]
    ):
        datafile: str = os.path.join(get_data_path(), "iris.csv")

        assert syphon.archive(archive_dir, [datafile], overwrite=True)
        assert not os.path.exists(os.path.join(get_data_path(), "#lock"))

        cache_file.write(rand_string())

        with pytest.raises(FileExistsError):
            syphon.build(
                cache_file,
                *get_data_files(archive_dir),
                hash_filepath=hash_file,
                incremental=False,
                overwrite=False,
                post_hash=False,
            )
        assert_post_hash(False, cache_file, hash_filepath=hash_file)

    @staticmethod
    def test_raises_fileexistserror_when_cache_exists_during_incremental_build(
        archive_dir: LocalPath, cache_file: LocalPath, hash_file: Optional[LocalPath]
    ):
        datafile: str = os.path.join(get_data_path(), "iris.csv")

        assert syphon.archive(archive_dir, [datafile], overwrite=True)
        assert not os.path.exists(os.path.join(get_data_path(), "#lock"))

        cache_file.write(rand_string())

        with pytest.raises(FileExistsError):
            syphon.build(
                cache_file,
                *get_data_files(archive_dir),
                hash_filepath=hash_file,
                incremental=True,
                overwrite=False,
                post_hash=False,
            )
        assert_post_hash(False, cache_file, hash_filepath=hash_file)
