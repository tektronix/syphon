"""syphon.tests.conftest.py

   Copyright (c) 2017-2018 Keithley Instruments, LLC.
   Licensed under MIT (https://github.com/ehall/syphon/blob/master/LICENSE)

"""
import pytest
from sortedcontainers import SortedDict, SortedList

from . import rand_string, UnitTestData

MAX_DATA_FILES = 4

@pytest.fixture
def import_dir(tmpdir):
    return tmpdir.mkdir('import')

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
