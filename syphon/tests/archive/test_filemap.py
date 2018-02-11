"""syphon.tests.archive.test_filemap.py

   Copyright (c) 2017-2018 Keithley Instruments, LLC.
   Licensed under MIT (https://github.com/ehall/syphon/blob/master/LICENSE)

"""
from sortedcontainers import SortedDict, SortedList

from syphon.archive import file_map

def test_multi_filemap(new_random_files):
    data = new_random_files['data']
    meta = new_random_files['meta']
    expected = new_random_files['filemap']

    str_data = SortedList()
    for d in data:
        str_data.add(str(d))

    str_meta = SortedList()
    for m in meta:
        str_meta.add(str(m))

    str_expected = SortedDict()
    for key in expected:
        match_list = expected[key]
        str_list = []
        for m in match_list:
            str_list.append(str(m))
        str_expected[key] = str_list

    actual = file_map(str_data, str_meta)

    assert actual == str_expected

def test_name_filemap(new_matching_files):
    data = new_matching_files['data']
    meta = new_matching_files['meta']
    expected = new_matching_files['filemap']

    str_data = SortedList()
    for d in data:
        str_data.add(str(d))

    str_meta = SortedList()
    for m in meta:
        str_meta.add(str(m))

    str_expected = SortedDict()
    for key in expected:
        match_list = expected[key]
        str_list = []
        for m in match_list:
            str_list.append(str(m))
        str_expected[key] = str_list

    actual = file_map(str_data, str_meta)

    assert actual == str_expected
