"""syphon.tests.conftest.py

   Copyright (c) 2017-2018 Keithley Instruments, LLC.
   Licensed under MIT (https://github.com/ehall/syphon/blob/master/LICENSE)

"""
import pytest
import random
from os import environ
from pandas.util.testing import makeCustomIndex
from sortedcontainers import SortedDict, SortedList

from . import rand_string, UnitTestData

MAX_DATA_FILES = 4
MAX_METADATA_COLS = 5
MAX_VALUES_PER_META_COL = 3

def pytest_addoption(parser):
    parser.addoption('--slow',
                     action='store_true',
                     default=False,
                     help='Run slow tests.')

def pytest_collection_modifyitems(config, items):
    if config.getoption('--slow'):
        skip_less = pytest.mark.skip(reason='Covered by slow tests.')
        for item in items:
            if 'less_coverage' in item.keywords:
                item.add_marker(skip_less)
        return
    slow_skip = pytest.mark.skip(reason='Need --slow flag to run.')
    for item in items:
        if 'slow' in item.keywords:
            item.add_marker(slow_skip)

@pytest.fixture(scope='session')
def seed():
    random.seed(a=int(environ['PYTHONHASHSEED']))

@pytest.fixture
def archive_dir(tmpdir):
    return tmpdir.mkdir('archive')

@pytest.fixture
def import_dir(tmpdir):
    return tmpdir.mkdir('import')

@pytest.fixture(params=[x for x in range(0, MAX_METADATA_COLS)])
def metadata_column_headers(request):
    """Make a list of metadata column headers.
    
    Returns:
        list: A metadata column header list whose length is between 0
            and `MAX_METADATA_COLS`.
    """
    if request.param is 0:
        return list()
    # pandas bug (?) in makeCustomIndex when nentries = 1
    elif request.param is 1:
        return ['M_l0_g0']
    else:
        return list(makeCustomIndex(request.param, 1, prefix='M'))

@pytest.fixture(params=[x for x in range(0, MAX_VALUES_PER_META_COL+1)])
def metadata_columns(request, metadata_column_headers):
    """Make a metadata column header and column value dictionary."""
    template = 'val{}'
    columns = {}
    for header in metadata_column_headers:
        columns[header] = []
        for i in range(0, request.param):
            columns[header].append(template.format(i))
    return columns

@pytest.fixture
def metadata_random_columns(seed, metadata_column_headers):
    """Make dictionary containing lists between 1 and
    `MAX_VALUES_PER_META_COL` in length."""
    def _rand_depth(max_: int):
        return random.randint(1, max_)

    template = 'val{}'
    columns = {}
    for header in metadata_column_headers:
        columns[header] = []
        for i in range(0, _rand_depth(MAX_VALUES_PER_META_COL)):
            columns[header].append(template.format(i))
    return columns

@pytest.fixture(params=[x for x in range(1, MAX_DATA_FILES)])
def new_datafiles(request, import_dir):
    test_data = UnitTestData()
    files = SortedList()
    for _ in range(request.param):
        new_file = import_dir
        files.add(new_file.join('{}.csv'.format(rand_string())))
    test_data.data_files = files
    return test_data

@pytest.fixture(params=[x for x in range(0, MAX_DATA_FILES*2)])
def new_random_files(request, import_dir, new_datafiles):
    files = SortedList()
    for _ in range(request.param):
        new_file = import_dir
        files.add(new_file.join('{}.meta'.format(rand_string())))
    new_datafiles.meta_files = files

    match_dict = SortedDict()
    for f in new_datafiles.data_files:
        match_dict[str(f)] = files
    new_datafiles.filemap = match_dict

    return new_datafiles

@pytest.fixture
def new_matching_files(new_datafiles):
    files = SortedList()
    match_dict = SortedDict()
    for f in new_datafiles.data_files:
        new_file = f.new(ext='meta')
        files.add(new_file)
        match_dict[str(f)] = [new_file]
    new_datafiles.meta_files = files
    new_datafiles.filemap = match_dict

    return new_datafiles

@pytest.fixture(params=[True, False])
def overwrite_fixture(request):
    return request.param
