"""syphon.tests.archive.test_filemap.py

   Copyright Keithley Instruments, LLC.
   Licensed under MIT (https://github.com/ehall/syphon/blob/master/LICENSE)

"""
from os.path import splitext

from sortedcontainers import SortedDict, SortedList

from syphon.archive import file_map


def test_filemap_loose_metadata(random_data, random_metadata):
    data = random_data
    meta = random_metadata

    expected = SortedDict()
    for d in data:
        expected[d] = SortedList(meta)

    actual = file_map(SortedList(data), SortedList(meta))

    assert actual == expected


def test_filemap_data_metadata_pairs(random_data):
    data = random_data

    meta = list()
    expected = SortedDict()
    for d in data:
        new_file = '{}{}'.format(splitext(d)[0], '.meta')
        meta.append(new_file)
        expected[d] = [new_file]

    actual = file_map(SortedList(data), SortedList(meta))

    assert actual == expected
