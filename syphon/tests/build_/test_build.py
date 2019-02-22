"""syphon.tests.build_.test_build.py

   Copyright Keithley Instruments, LLC.
   Licensed under MIT (https://github.com/tektronix/syphon/blob/master/LICENSE)

"""
import os

import pytest
from pandas import DataFrame, read_csv
from pandas.testing import assert_frame_equal
from sortedcontainers import SortedDict
from syphon import Context
from syphon.archive import archive
from syphon.init import init
from syphon.build_ import build

from .. import get_data_path


class TestBuild(object):
    @staticmethod
    def _delete_cache(file: str):
        try:
            os.remove(file)
        except OSError:
            raise

    def test_build_iris(self, archive_dir, cache_file, overwrite):
        try:
            TestBuild._delete_cache(str(cache_file))
        except FileNotFoundError:
            pass
        except OSError:
            raise

        context = Context()
        context.archive = str(archive_dir)
        context.cache = str(cache_file)
        context.data = os.path.join(get_data_path(), 'iris.csv')
        context.overwrite = overwrite
        context.schema = SortedDict({'0': 'Name'})
        context.verbose = True

        init(context)
        archive(context)
        assert not os.path.exists(os.path.join(get_data_path(), '#lock'))

        expected_frame = DataFrame(read_csv(context.data))

        if context.overwrite:
            with open(context.cache, mode='w') as f:
                f.write('content')

        build(context)

        actual_frame = DataFrame(read_csv(context.cache))

        expected_frame = expected_frame.reindex_like(actual_frame)

        equal_shapes = expected_frame.shape == actual_frame.shape
        equal_indices = (expected_frame.index).equals(actual_frame.index)
        equal_columns = (expected_frame.columns).equals(actual_frame.columns)

        if not equal_shapes:
            print('unequal shapes: expected {0} found {1}'.format(
                expected_frame.shape, actual_frame.shape))

        if not equal_indices:
            print('unequal indices: expected {0} found {1}'.format(
                expected_frame.index, actual_frame.index))

        if not equal_columns:
            print('unequal columns: expected {0} found {1}'.format(
                expected_frame.columns, actual_frame.columns))

        for i, col in enumerate(expected_frame.columns):
            if col in actual_frame:
                expected_col = expected_frame.iloc[:, i]
                actual_col = actual_frame.iloc[:, i]
                equal_names = expected_col.name == actual_col.name
                equal_lengths = len(expected_col) == len(actual_col)
                equal_indices = (expected_col.index).equals(actual_col.index)

                if not equal_names:
                    print('  col {0}: unequal names: expected {1} found {2}'
                          .format(i, expected_col.name, actual_col.name))

                if not equal_lengths:
                    print('  col {0}: unequal lengths: expected {1} found {2}'
                          .format(i, len(expected_col), len(actual_col)))

                if not equal_indices:
                    print('  col {0}: unequal indices: expected {1} found {3}'
                          .format(i, expected_col.index, actual_col.index))

                if equal_lengths:
                    for j in range(expected_col.size):
                        if expected_col[j] != actual_col[j]:
                            msg = '  col {0}: unequal @ row {1}: '
                            msg += 'expected {2} found {3}'
                            print(msg.format(
                                i, j, expected_col[j], actual_col[j]))

        assert_frame_equal(expected_frame, actual_frame, check_exact=True)

    def test_build_iris_no_schema(self, archive_dir, cache_file, overwrite):
        try:
            TestBuild._delete_cache(str(cache_file))
        except FileNotFoundError:
            pass
        except OSError:
            raise

        context = Context()
        context.archive = str(archive_dir)
        context.cache = str(cache_file)
        context.data = os.path.join(get_data_path(), 'iris.csv')
        context.overwrite = overwrite
        context.schema = SortedDict()

        archive(context)
        assert not os.path.exists(os.path.join(get_data_path(), '#lock'))

        expected_frame = DataFrame(read_csv(context.data, dtype=str))

        if context.overwrite:
            with open(context.cache, mode='w') as f:
                f.write('content')

        build(context)

        actual_frame = DataFrame(read_csv(context.cache, dtype=str))

        assert_frame_equal(expected_frame, actual_frame, check_like=True)

    def test_build_fileexistserror(self, archive_dir, cache_file):
        try:
            TestBuild._delete_cache(str(cache_file))
        except FileNotFoundError:
            pass
        except OSError:
            raise

        context = Context()
        context.archive = str(archive_dir)
        context.cache = str(cache_file)
        context.data = os.path.join(get_data_path(), 'iris.csv')
        context.overwrite = False
        context.schema = SortedDict()

        archive(context)
        assert not os.path.exists(os.path.join(get_data_path(), '#lock'))

        with open(context.cache, mode='w') as f:
            f.write('content')

        with pytest.raises(FileExistsError):
            build(context)
