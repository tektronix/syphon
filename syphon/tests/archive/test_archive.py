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


@pytest.fixture(params=[
    (
        'iris.csv',
        SortedDict({'0': 'Name'})
    ),
    (
        'iris_plus.csv',
        SortedDict({'0': 'Species', '1': 'PetalColor'})
    ),
    (
        'auto-mpg.csv',
        SortedDict({'0': 'model year', '1': 'cylinders', '2': 'origin'})
    )
])
def archive_params(request):
    return request.param


def _get_expected_paths(
        path: str, schema: SortedDict, subset: DataFrame, filename: str,
        path_list=None) -> SortedList:
    # prevent mutable default parameter
    if path_list is None:
        path_list = SortedList()

    this_schema = schema.copy()
    header = None
    try:
        _, header = this_schema.popitem(last=False)
    except KeyError:
        path_list.add(os.path.join(path, filename))
        return path_list

    if header not in subset.columns:
        return path_list

    for value in subset.get(header).drop_duplicates().values:
        new_subset = subset.loc[subset.get(header) == value]
        value = value.lower().replace(' ', '_')
        if value[-1] == '.':
            value = value[:-1]
        path_list = _get_expected_paths(
            os.path.join(path, value),
            this_schema,
            new_subset,
            filename,
            path_list=path_list)
    return path_list


def test_archive(archive_params, archive_dir, overwrite):
    filename, schema = archive_params

    context = Context()
    context.archive = str(archive_dir)
    context.data = os.path.join(get_data_path(), filename)
    context.overwrite = overwrite
    context.schema = schema

    init(context)

    expected_df = DataFrame(read_csv(context.data, dtype=str))
    expected_df.sort_values(list(expected_df.columns), inplace=True)
    expected_df.reset_index(drop=True, inplace=True)

    expected_paths = _get_expected_paths(
        context.archive,
        schema,
        expected_df,
        filename
    )

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


def test_archive_no_schema(archive_params, archive_dir, overwrite):
    filename, _ = archive_params

    context = Context()
    context.archive = str(archive_dir)
    context.data = os.path.join(get_data_path(), filename)
    context.overwrite = overwrite
    context.schema = SortedDict()

    expected_df = DataFrame(read_csv(context.data, dtype=str))
    expected_df.sort_values(list(expected_df.columns), inplace=True)
    expected_df.reset_index(drop=True, inplace=True)

    expected_paths = SortedList([
        os.path.join(context.archive, filename)
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


def test_archive_fileexistserror(archive_params, archive_dir):
    filename, schema = archive_params

    context = Context()
    context.archive = str(archive_dir)
    context.data = os.path.join(get_data_path(), filename)
    context.overwrite = False
    context.schema = schema

    init(context)

    expected_df = DataFrame(read_csv(context.data, dtype=str))

    expected_paths = _get_expected_paths(
        context.archive,
        schema,
        expected_df,
        filename
    )

    for e in expected_paths:
        os.makedirs(os.path.dirname(e), exist_ok=True)
        with open(e, mode='w') as f:
            f.write('content')

    with pytest.raises(FileExistsError):
        archive(context)

    try:
        os.remove(os.path.join(get_data_path(), '#lock'))
    except OSError:
        raise
