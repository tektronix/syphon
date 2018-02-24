"""syphon.tests.schema.test_save.py

   Copyright (c) 2017-2018 Keithley Instruments, LLC.
   Licensed under MIT (https://github.com/ehall/syphon/blob/master/LICENSE)

"""
import pytest
from json import dumps, loads
from sortedcontainers import SortedDict

from syphon.schema import save

class TestSave(object):
    multi_schema = SortedDict({'0': 'column2', '1': 'column4'})
    single_schema = SortedDict({'0': 'column1'})

    @pytest.mark.parametrize('schema, overwrite', [
        (single_schema, False),
        (multi_schema, True)
    ])
    def test_save_new(self, schema, overwrite, tmpdir):
        tmpfile = tmpdir.mkdir('test_save').join('.schema.json')

        save(schema, str(tmpfile), overwrite)

        assert SortedDict(loads(tmpfile.read())) == schema

    @pytest.mark.parametrize('schema', [
        (single_schema),
        (multi_schema)
    ])
    def test_save_overwrite(self, schema, tmpdir):
        tmpfile = tmpdir.mkdir('test_save').join('.schema.json')
        tmpfile.write('content')

        save(schema, str(tmpfile), True)

        assert SortedDict(loads(tmpfile.read())) == schema

    def test_save_fileexistserror(self, tmpdir):
        tmpfile = tmpdir.mkdir('test_save').join('.schema.json')
        tmpfile.write('content')

        with pytest.raises(FileExistsError):
            save(TestSave.single_schema, str(tmpfile), False)
