"""syphon.init.test_init.py

   Copyright (c) 2017-2018 Keithley Instruments, LLC.
   Licensed under MIT (https://github.com/ehall/syphon/blob/master/LICENSE)

"""
from os.path import join

import pytest
from json import loads
from sortedcontainers import SortedDict

from syphon import Context
from syphon.init import init

@pytest.fixture
def archive_fixture(tmpdir):
    return tmpdir.mkdir('archive')

@pytest.fixture(params=[
    {'0': 'column1'},
    {'0': 'column2', '1': 'column4'},
    {'0': 'column1', '1': 'column3', '2': 'column4'},
])
def schema_fixture(request):
    return SortedDict(request.param)

@pytest.fixture(params=[True, False])
def overwrite_fixture(request):
    return request.param

@pytest.fixture
def context_fixture(archive_fixture, schema_fixture, overwrite_fixture):
    context = Context()
    context.archive = archive_fixture
    context.schema = schema_fixture
    context.overwrite = overwrite_fixture
    return context

def test_init(context_fixture):
    init(context_fixture)

    schema_path = join(context_fixture.archive, context_fixture.schema_file)
    actual = None
    with open(schema_path, 'r') as f:
        actual = SortedDict(loads(f.read()))

    assert actual == context_fixture.schema
