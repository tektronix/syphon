"""tests.schema.test_save.py

   Copyright Keithley Instruments, LLC.
   Licensed under MIT (https://github.com/tektronix/syphon/blob/master/LICENSE)

"""
from json import loads

import pytest
from py._path.local import LocalPath
from sortedcontainers import SortedDict

from syphon.schema import save


class TestSave(object):
    multi_schema = SortedDict({"0": "column2", "1": "column4"})
    single_schema = SortedDict({"0": "column1"})

    @pytest.mark.parametrize(
        "schema, overwrite", [(single_schema, False), (multi_schema, True)]
    )
    def test_save_new(self, schema: SortedDict, overwrite: bool, tmpdir: LocalPath):
        tmpfile: LocalPath = tmpdir.mkdir("test_save").join(".schema.json")

        save(schema, str(tmpfile), overwrite)

        assert SortedDict(loads(tmpfile.read())) == schema

    @pytest.mark.parametrize("schema", [(single_schema), (multi_schema)])
    def test_save_overwrite(self, schema: SortedDict, tmpdir: LocalPath):
        tmpfile: LocalPath = tmpdir.mkdir("test_save").join(".schema.json")
        tmpfile.write("content")

        save(schema, str(tmpfile), True)

        assert SortedDict(loads(tmpfile.read())) == schema

    def test_save_fileexistserror(self, tmpdir: LocalPath):
        tmpfile: LocalPath = tmpdir.mkdir("test_save").join(".schema.json")
        tmpfile.write("content")

        with pytest.raises(FileExistsError):
            save(TestSave.single_schema, str(tmpfile), False)
