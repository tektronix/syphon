"""syphon.tests.archive.test_archive.py

   Copyright (c) 2017-2018 Keithley Instruments, LLC.
   Licensed under MIT (https://github.com/ehall/syphon/blob/master/LICENSE)

"""
import os

import pytest
from pandas import concat, DataFrame, read_csv
from pandas.testing import assert_frame_equal
from sortedcontainers import SortedDict, SortedList
from syphon import Context
from syphon.archive import archive
from syphon.init import init

from .. import get_data_path

class TestArchive(object):
    def test_archive_iris(self, archive_dir, overwrite_fixture):
        context = Context()
        context.archive = archive_dir
        context.data = os.path.join(get_data_path(), 'iris.csv')
        context.overwrite = overwrite_fixture
        context.schema = SortedDict({'0': 'Name'})

        init(context)

        expected_frame = DataFrame(read_csv(context.data, dtype=str))

        expected_paths = SortedList([
            os.path.join(str(context.archive), 'iris-setosa', 'iris.csv'),
            os.path.join(str(context.archive), 'iris-versicolor', 'iris.csv'),
            os.path.join(str(context.archive), 'iris-virginica', 'iris.csv')
        ])

        if context.overwrite:
            for e in expected_paths:
                path = archive_dir.new()
                path.mkdir(os.path.basename(os.path.dirname(e)))
                with open(e, mode='w') as f:
                    f.write('content')

        archive(context)

        actual_frame = DataFrame()
        actual_paths = SortedList()
        for root, _, files in os.walk(context.archive):
            for f in files:
                if '.csv' in f:
                    filepath = os.path.join(root, f)
                    actual_paths.add(filepath)
                    actual_frame = concat([
                        actual_frame,
                        DataFrame(read_csv(filepath, dtype=str))
                    ])

        actual_frame.reset_index(drop=True, inplace=True)

        assert expected_paths == actual_paths
        assert_frame_equal(expected_frame, actual_frame)

    def test_archive_iris_no_schema(self, archive_dir, overwrite_fixture):
        context = Context()
        context.archive = archive_dir
        context.data = os.path.join(get_data_path(), 'iris.csv')
        context.overwrite = overwrite_fixture
        context.schema = SortedDict()

        expected_frame = DataFrame(read_csv(context.data, dtype=str))

        expected_paths = SortedList([
            os.path.join(str(context.archive), 'iris.csv')
        ])

        if context.overwrite:
            for e in expected_paths:
                path = archive_dir.new()
                path.mkdir(os.path.basename(os.path.dirname(e)))
                with open(e, mode='w') as f:
                    f.write('content')

        archive(context)

        actual_frame = DataFrame()
        actual_paths = SortedList()
        for root, _, files in os.walk(context.archive):
            for f in files:
                if '.csv' in f:
                    filepath = os.path.join(root, f)
                    actual_paths.add(filepath)
                    actual_frame = concat([
                        actual_frame,
                        DataFrame(read_csv(filepath, dtype=str))
                    ])

        actual_frame.reset_index(drop=True, inplace=True)

        assert expected_paths == actual_paths
        assert_frame_equal(expected_frame, actual_frame)

    def test_archive_fileexistserror(self, archive_dir):
        context = Context()
        context.archive = archive_dir
        context.data = os.path.join(get_data_path(), 'iris.csv')
        context.overwrite = False
        context.schema = SortedDict({'0': 'Name'})

        init(context)

        expected_paths = SortedList([
            os.path.join(str(context.archive), 'iris-setosa', 'iris.csv'),
            os.path.join(str(context.archive), 'iris-versicolor', 'iris.csv'),
            os.path.join(str(context.archive), 'iris-virginica', 'iris.csv')
        ])

        for e in expected_paths:
            path = archive_dir.new()
            path.mkdir(os.path.basename(os.path.dirname(e)))
            with open(e, mode='w') as f:
                f.write('content')

        with pytest.raises(FileExistsError):
            archive(context)

        try:
            os.remove(os.path.join(get_data_path(), '#lock'))
        except:
            raise
