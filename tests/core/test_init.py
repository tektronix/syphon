"""tests.test_init.py

   Copyright Keithley Instruments, LLC.
   Licensed under MIT (https://github.com/tektronix/syphon/blob/master/LICENSE)

"""
import os
from json import loads

import pytest
from _pytest.capture import CaptureFixture
from _pytest.fixtures import FixtureRequest
from py._path.local import LocalPath
from sortedcontainers import SortedDict

import syphon
import syphon.schema

from ..assert_utils import assert_captured_outerr


@pytest.fixture(
    params=[
        {"0": "column1"},
        {"0": "column2", "1": "column4"},
        {"0": "column1", "1": "column3", "2": "column4"},
    ]
)
def init_schema_fixture(request: FixtureRequest) -> SortedDict:
    return SortedDict(request.param)


def test_init(
    capsys: CaptureFixture,
    archive_dir: LocalPath,
    init_schema_fixture: SortedDict,
    overwrite: bool,
    verbose: bool,
):
    schemafile = os.path.join(archive_dir, syphon.schema.DEFAULT_FILE)

    syphon.init(init_schema_fixture, schemafile, overwrite, verbose)

    with open(schemafile, "r") as f:
        actual = SortedDict(loads(f.read()))

    assert actual == init_schema_fixture

    assert_captured_outerr(capsys.readouterr(), verbose, False)


def test_init_fileexistserror(archive_dir: LocalPath, init_schema_fixture: SortedDict):
    schemafile = os.path.join(archive_dir, syphon.schema.DEFAULT_FILE)

    with open(schemafile, mode="w") as f:
        f.write("content")

    with pytest.raises(FileExistsError):
        syphon.init(init_schema_fixture, schemafile, overwrite=False)
