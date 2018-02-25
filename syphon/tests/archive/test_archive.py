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
from syphon.schema.resolvepath import _normalize

from .. import get_data_path

class TestArchiveIris(object):
    filename = 'iris.csv'
    schema = SortedDict({'0': 'Name'})

    def test_archive(self, archive_dir, overwrite):
        context = Context()
        context.archive = str(archive_dir)
        context.data = os.path.join(get_data_path(), self.filename)
        context.overwrite = overwrite
        context.schema = self.schema

        init(context)

        expected_df = DataFrame(read_csv(context.data, dtype=str))
        expected_df.sort_values(list(expected_df.columns), inplace=True)
        expected_df.reset_index(drop=True, inplace=True)

        expected_paths = SortedList()
        for name in expected_df[self.schema['0']].drop_duplicates().values:
            expected_paths.add(os.path.join(
                context.archive,
                _normalize(name),
                self.filename
            ))

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

        actual_frame.sort_values(list(actual_frame.columns), inplace=True)
        actual_frame.reset_index(drop=True, inplace=True)

        assert expected_paths == actual_paths
        assert_frame_equal(expected_df, actual_frame)

    def test_archive_no_schema(self, archive_dir, overwrite):
        context = Context()
        context.archive = str(archive_dir)
        context.data = os.path.join(get_data_path(), self.filename)
        context.overwrite = overwrite
        context.schema = SortedDict()

        expected_df = DataFrame(read_csv(context.data, dtype=str))
        expected_df.sort_values(list(expected_df.columns), inplace=True)
        expected_df.reset_index(drop=True, inplace=True)

        expected_paths = SortedList([
            os.path.join(context.archive, self.filename)
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

        actual_frame.sort_values(list(actual_frame.columns), inplace=True)
        actual_frame.reset_index(drop=True, inplace=True)

        assert expected_paths == actual_paths
        assert_frame_equal(expected_df, actual_frame)

    def test_archive_fileexistserror(self, archive_dir):
        context = Context()
        context.archive = str(archive_dir)
        context.data = os.path.join(get_data_path(), self.filename)
        context.overwrite = False
        context.schema = self.schema

        init(context)

        expected_df = DataFrame(read_csv(context.data, dtype=str))

        expected_paths = SortedList()
        for name in expected_df[self.schema['0']].drop_duplicates().values:
            expected_paths.add(os.path.join(
                context.archive,
                _normalize(name),
                self.filename
            ))

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

class TestArchiveIrisPlus(object):
    filename = 'iris_plus.csv'
    schema = SortedDict({'0': 'Species', '1': 'PetalColor'})

    def test_archive(self, archive_dir, overwrite):
        context = Context()
        context.archive = str(archive_dir)
        context.data = os.path.join(get_data_path(), self.filename)
        context.overwrite = overwrite
        context.schema = self.schema

        init(context)

        expected_df = DataFrame(read_csv(context.data, dtype=str))
        expected_df.sort_values(list(expected_df.columns), inplace=True)
        expected_df.reset_index(drop=True, inplace=True)

        expected_paths = SortedList()
        for species in expected_df[self.schema['0']].drop_duplicates().values:
            subset = expected_df.loc[expected_df[self.schema['0']] == species]
            for color in subset[self.schema['1']].drop_duplicates().values:
                expected_paths.add(os.path.join(
                    context.archive,
                    _normalize(species),
                    _normalize(color),
                    self.filename
                ))

        if context.overwrite:
            for e in expected_paths:
                os.makedirs(os.path.dirname(e), exist_ok=True)
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

        actual_frame.sort_values(list(actual_frame.columns), inplace=True)
        actual_frame.reset_index(drop=True, inplace=True)

        assert expected_paths == actual_paths
        assert_frame_equal(expected_df, actual_frame)

    def test_archive_no_schema(self, archive_dir, overwrite):
        context = Context()
        context.archive = str(archive_dir)
        context.data = os.path.join(get_data_path(), self.filename)
        context.overwrite = overwrite
        context.schema = SortedDict()

        expected_df = DataFrame(read_csv(context.data, dtype=str))
        expected_df.sort_values(list(expected_df.columns), inplace=True)
        expected_df.reset_index(drop=True, inplace=True)

        expected_paths = SortedList([
            os.path.join(context.archive, self.filename)
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

        actual_frame.sort_values(list(actual_frame.columns), inplace=True)
        actual_frame.reset_index(drop=True, inplace=True)

        assert expected_paths == actual_paths
        assert_frame_equal(expected_df, actual_frame)

    def test_archive_fileexistserror(self, archive_dir):
        context = Context()
        context.archive = str(archive_dir)
        context.data = os.path.join(get_data_path(), self.filename)
        context.overwrite = False
        context.schema = self.schema

        init(context)

        expected_df = DataFrame(read_csv(context.data, dtype=str))

        expected_paths = SortedList()
        for species in expected_df[self.schema['0']].drop_duplicates().values:
            subset = expected_df.loc[expected_df[self.schema['0']] == species]
            for color in subset[self.schema['1']].drop_duplicates().values:
                expected_paths.add(os.path.join(
                    context.archive,
                    _normalize(species),
                    _normalize(color),
                    self.filename
                ))

        for e in expected_paths:
            os.makedirs(os.path.dirname(e), exist_ok=True)
            with open(e, mode='w') as f:
                f.write('content')

        with pytest.raises(FileExistsError):
            archive(context)

        try:
            os.remove(os.path.join(get_data_path(), '#lock'))
        except:
            raise
