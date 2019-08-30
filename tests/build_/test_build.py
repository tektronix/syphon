"""syphon.tests.build_.test_build.py

   Copyright Keithley Instruments, LLC.
   Licensed under MIT (https://github.com/tektronix/syphon/blob/master/LICENSE)

"""
import os

import pytest
from pandas import DataFrame, read_csv
from pandas.testing import assert_frame_equal
from py._path.local import LocalPath
from sortedcontainers import SortedDict

from syphon import Context
from syphon.archive import archive
from syphon.build_ import build
from syphon.init import init

from .. import get_data_path


class TestBuild(object):
    @staticmethod
    def _delete_cache(file: str):
        try:
            os.remove(file)
        except OSError:
            raise

    def test_build_iris(
        self, archive_dir: LocalPath, cache_file: LocalPath, overwrite: bool
    ):
        try:
            TestBuild._delete_cache(str(cache_file))
        except FileNotFoundError:
            pass
        except OSError:
            raise

        context = Context()
        context.archive = str(archive_dir)
        context.cache = str(cache_file)
        context.data = os.path.join(get_data_path(), "iris.csv")
        context.overwrite = overwrite
        context.schema = SortedDict({"0": "Name"})
        context.verbose = True

        init(context)
        archive(context)
        assert not os.path.exists(os.path.join(get_data_path(), "#lock"))

        expected_frame = DataFrame(read_csv(context.data, index_col="Index"))
        expected_frame.sort_index(inplace=True)

        if context.overwrite:
            with open(context.cache, mode="w") as f:
                f.write("content")

        build(context)

        actual_frame = DataFrame(read_csv(context.cache, index_col="Index"))
        actual_frame.sort_index(inplace=True)

        assert (
            expected_frame.shape == actual_frame.shape
        ), "unequal shapes: expected {0} found {1}".format(
            expected_frame.shape, actual_frame.shape
        )
        assert (expected_frame.index).equals(
            actual_frame.index
        ), "unequal indices: expected {0} found {1}".format(
            expected_frame.index, actual_frame.index
        )
        assert (expected_frame.columns).equals(
            actual_frame.columns
        ), "unequal columns: expected {0} found {1}".format(
            expected_frame.columns, actual_frame.columns
        )

        for i, col in enumerate(expected_frame.columns):
            if col in actual_frame:
                expected_col = expected_frame.iloc[:, i]
                actual_col = actual_frame.iloc[:, i]

                lengths_equal: bool = len(expected_col) == len(actual_col)

                assert (
                    expected_col.name == actual_col.name
                ), "  col {0}: unequal names: expected {1} found {2}".format(
                    i, expected_col.name, actual_col.name
                )
                assert (
                    lengths_equal
                ), "  col {0}: unequal lengths: expected {1} found {2}".format(
                    i, len(expected_col), len(actual_col)
                )
                assert (expected_col.index).equals(
                    actual_col.index
                ), "  col {0}: unequal indices: expected {1} found {3}".format(
                    i, expected_col.index, actual_col.index
                )

                if lengths_equal:
                    for j in range(expected_col.size):
                        if expected_col[j] != actual_col[j]:
                            print(
                                " ".join(
                                    [
                                        "  col {0}: unequal @ row {1}:".format(i, j),
                                        "expected {2} found {3}".format(
                                            expected_col[j], actual_col[j]
                                        ),
                                    ]
                                )
                            )

        assert_frame_equal(expected_frame, actual_frame, check_exact=True)

    def test_build_iris_no_schema(
        self, archive_dir: LocalPath, cache_file: LocalPath, overwrite: bool
    ):
        try:
            TestBuild._delete_cache(str(cache_file))
        except FileNotFoundError:
            pass
        except OSError:
            raise

        context = Context()
        context.archive = str(archive_dir)
        context.cache = str(cache_file)
        context.data = os.path.join(get_data_path(), "iris.csv")
        context.overwrite = overwrite
        context.schema = SortedDict()

        archive(context)
        assert not os.path.exists(os.path.join(get_data_path(), "#lock"))

        expected_frame = DataFrame(read_csv(context.data, dtype=str))

        if context.overwrite:
            with open(context.cache, mode="w") as f:
                f.write("content")

        build(context)

        actual_frame = DataFrame(read_csv(context.cache, dtype=str))

        assert_frame_equal(expected_frame, actual_frame, check_like=True)

    def test_build_fileexistserror(self, archive_dir: LocalPath, cache_file: LocalPath):
        try:
            TestBuild._delete_cache(str(cache_file))
        except FileNotFoundError:
            pass
        except OSError:
            raise

        context = Context()
        context.archive = str(archive_dir)
        context.cache = str(cache_file)
        context.data = os.path.join(get_data_path(), "iris.csv")
        context.overwrite = False
        context.schema = SortedDict()

        archive(context)
        assert not os.path.exists(os.path.join(get_data_path(), "#lock"))

        with open(context.cache, mode="w") as f:
            f.write("content")

        with pytest.raises(FileExistsError):
            build(context)
