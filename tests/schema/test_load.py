"""tests.schema.test_load.py

   Copyright Keithley Instruments, LLC.
   Licensed under MIT (https://github.com/tektronix/syphon/blob/master/LICENSE)

"""
from json import dumps, loads

import pytest
from py._path.local import LocalPath
from sortedcontainers import SortedDict

from syphon.schema import load


class TestLoad(object):
    multi_schema = SortedDict({"0": "column2", "1": "column4"})
    single_schema = SortedDict({"0": "column1"})

    @pytest.mark.parametrize("schema", [(single_schema), (multi_schema)])
    def test_load(self, schema: SortedDict, tmpdir: LocalPath):
        tmpfile: LocalPath = tmpdir.mkdir("test_load").join(".schema.json")
        tmpfile.write(dumps(schema))

        actual: SortedDict = load(str(tmpfile))

        assert SortedDict(loads(tmpfile.read())) == actual
