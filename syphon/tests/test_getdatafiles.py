"""syphon.tests.test_getdatafiles.py

   Copyright (c) 2017-2018 Keithley Instruments, LLC.
   Licensed under MIT (https://github.com/ehall/syphon/blob/master/LICENSE)

"""
from syphon import get_data_files

def test_absolute_path(dataset_factory):
    import re
    from os import walk
    from os.path import abspath, join

    # make regex file pattern matcher
    regex = re.compile('.*\.csv')

    expected_list = []
    # get CSV files manually
    for root, _, files in walk(abspath(dataset_factory)):
        for f in files:
            if regex.match(f):
                expected_list.append(join(root, f))
        break

    # test
    actual_list = get_data_files(abspath(dataset_factory), '.csv')

    # check
    assert set(actual_list) == set(expected_list)

def test_relative_path(dataset_factory):
    import re
    from os import walk
    from os.path import dirname, join, relpath

    # make regex file pattern matcher
    regex = re.compile('.*\.csv')

    # get relative path to the temp directory
    path = relpath(dataset_factory, start=dirname(__file__))

    expected_list = []
    # get CSV files manually
    for root, _, files in walk(path):
        for f in files:
            if regex.match(f):
                expected_list.append(join(root, f))
        break

    # test
    actual_list = get_data_files(path, '.csv')

    assert set(actual_list) == set(expected_list)
