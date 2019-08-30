"""syphon.tests.archive.test_filemap.py

   Copyright Keithley Instruments, LLC.
   Licensed under MIT (https://github.com/tektronix/syphon/blob/master/LICENSE)

"""
from os.path import splitext
from typing import List

from sortedcontainers import SortedDict, SortedList

from syphon.archive import file_map


def test_filemap_loose_metadata(random_data: List[str], random_metadata: List[str]):
    data = random_data
    meta = random_metadata

    expected = SortedDict()
    for d in data:
        expected[d] = SortedList(meta)

    actual: SortedDict = file_map(SortedList(data), SortedList(meta))

    assert actual == expected


def test_filemap_data_metadata_pairs(random_data: List[str]):
    data = random_data

    meta: List[str] = list()
    expected = SortedDict()
    for d in data:
        new_file = "{}{}".format(splitext(d)[0], ".meta")
        meta.append(new_file)
        expected[d] = [new_file]

    actual: SortedDict = file_map(SortedList(data), SortedList(meta))

    assert actual == expected
