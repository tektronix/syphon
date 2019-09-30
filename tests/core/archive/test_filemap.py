"""tests.core.archive.test_filemap.py

   Copyright Keithley Instruments, LLC.
   Licensed under MIT (https://github.com/tektronix/syphon/blob/master/LICENSE)

"""
import os
from glob import glob
from typing import Dict, List

import pytest
from py._path.local import LocalPath

from syphon.core.archive.filemap import MappingBehavior, filemap

from ... import get_data_path, rand_string, randomize


class TestFilemap(object):
    @staticmethod
    @pytest.mark.parametrize("d", [n for n in range(1, 5)])
    def test_one_to_many_does_not_need_metadata_files(d: int):
        datafiles: List[str] = [rand_string() for _ in range(d)]
        metafiles: List[str] = []

        actual_filemap: Dict[str, List[str]] = filemap(
            MappingBehavior.ONE_TO_MANY, datafiles, metafiles
        )
        assert datafiles == [k for k in actual_filemap.keys()]
        for k in actual_filemap.keys():
            assert metafiles == actual_filemap[k]

    @staticmethod
    @pytest.mark.parametrize("d", [n for n in range(1, 5)])
    def test_one_to_many_groups_all_meta_to_each_data(d: int):
        datafiles: List[str] = [rand_string() for _ in range(d)]
        metafiles: List[str] = glob(
            os.path.join(get_data_path(), "iris-part-*-of-6.meta")
        )

        actual_filemap: Dict[str, List[str]] = filemap(
            MappingBehavior.ONE_TO_MANY, datafiles, metafiles
        )
        assert datafiles == [k for k in actual_filemap.keys()]
        for k in actual_filemap.keys():
            assert metafiles == actual_filemap[k]

    @staticmethod
    def test_one_to_one_lists_must_be_equal_size():
        datafiles: List[str] = glob(
            os.path.join(get_data_path(), "iris-part-*-of-6.csv")
        )
        metafiles: List[str] = glob(
            os.path.join(get_data_path(), "iris-part-*-of-6.meta")
        )
        metafiles = metafiles[:-1]

        expected_filemap = dict()
        actual_filemap: Dict[str, List[str]] = filemap(
            MappingBehavior.ONE_TO_ONE, datafiles, metafiles
        )
        assert expected_filemap == actual_filemap

    @staticmethod
    def test_one_to_one_only_compares_filenames(import_dir: LocalPath):
        datafiles: List[str] = randomize(
            *glob(os.path.join(get_data_path(), "iris-part-*-of-6.csv"))
        )
        target_metafiles: List[str] = glob(
            os.path.join(get_data_path(), "iris-part-*-of-6.meta")
        )
        metafiles: List[str] = []
        for meta in target_metafiles:
            dest = import_dir.join(os.path.basename(meta))
            metafiles.append(str(dest))
            LocalPath(meta).copy(dest)
        metafiles = randomize(*metafiles)

        datapath = LocalPath(get_data_path())
        expected_filemap: Dict[str, List[str]] = {
            str(datapath.join("iris-part-1-of-6.csv")): [
                str(import_dir.join("iris-part-1-of-6.meta"))
            ],
            str(datapath.join("iris-part-2-of-6.csv")): [
                str(import_dir.join("iris-part-2-of-6.meta"))
            ],
            str(datapath.join("iris-part-3-of-6.csv")): [
                str(import_dir.join("iris-part-3-of-6.meta"))
            ],
            str(datapath.join("iris-part-4-of-6.csv")): [
                str(import_dir.join("iris-part-4-of-6.meta"))
            ],
            str(datapath.join("iris-part-5-of-6.csv")): [
                str(import_dir.join("iris-part-5-of-6.meta"))
            ],
            str(datapath.join("iris-part-6-of-6.csv")): [
                str(import_dir.join("iris-part-6-of-6.meta"))
            ],
        }

        actual_filemap: Dict[str, List[str]] = filemap(
            MappingBehavior.ONE_TO_ONE, datafiles, metafiles
        )
        for k in actual_filemap:
            actual_filemap[k].sort()

        assert expected_filemap == actual_filemap

    @staticmethod
    def test_one_to_one_pairs_equal_filenames():
        datafiles: List[str] = randomize(
            *glob(os.path.join(get_data_path(), "iris-part-*-of-6.csv"))
        )
        metafiles: List[str] = randomize(
            *glob(os.path.join(get_data_path(), "iris-part-*-of-6.meta"))
        )

        datapath = LocalPath(get_data_path())
        expected_filemap: Dict[str, List[str]] = {
            str(datapath.join("iris-part-1-of-6.csv")): [
                str(datapath.join("iris-part-1-of-6.meta"))
            ],
            str(datapath.join("iris-part-2-of-6.csv")): [
                str(datapath.join("iris-part-2-of-6.meta"))
            ],
            str(datapath.join("iris-part-3-of-6.csv")): [
                str(datapath.join("iris-part-3-of-6.meta"))
            ],
            str(datapath.join("iris-part-4-of-6.csv")): [
                str(datapath.join("iris-part-4-of-6.meta"))
            ],
            str(datapath.join("iris-part-5-of-6.csv")): [
                str(datapath.join("iris-part-5-of-6.meta"))
            ],
            str(datapath.join("iris-part-6-of-6.csv")): [
                str(datapath.join("iris-part-6-of-6.meta"))
            ],
        }

        actual_filemap: Dict[str, List[str]] = filemap(
            MappingBehavior.ONE_TO_ONE, datafiles, metafiles
        )
        for k in actual_filemap:
            actual_filemap[k].sort()

        assert expected_filemap == actual_filemap

    @staticmethod
    def test_one_to_one_returns_empty_dict_on_bad_map():
        actual_filemap: Dict = filemap(MappingBehavior.ONE_TO_ONE, [rand_string()], [])
        assert {} == actual_filemap
