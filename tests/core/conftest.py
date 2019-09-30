"""tests.core.conftest.py

   Copyright Keithley Instruments, LLC.
   Licensed under MIT (https://github.com/tektronix/syphon/blob/master/LICENSE)

"""
from typing import Optional

import pytest
from _pytest.fixtures import FixtureRequest
from py._path.local import LocalPath


@pytest.fixture(params=[True, False])
def hash_file(request: FixtureRequest, hash_file: LocalPath) -> Optional[LocalPath]:
    """Return None if request.param == True else return the hash_file.

    If None, then the hash file ought to resolve to its default value.
    """
    return None if request.param else hash_file
