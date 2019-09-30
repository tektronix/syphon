"""tests.hash.conftest.py

   Copyright Keithley Instruments, LLC.
   Licensed under MIT (https://github.com/tektronix/syphon/blob/master/LICENSE)

"""
import hashlib
from typing import Optional

import pytest
from _pytest.fixtures import FixtureRequest


@pytest.fixture(params=["empty.csv", "iris.csv", "iris_plus.csv"])
def data_file(request: FixtureRequest) -> str:
    return request.param


@pytest.fixture(params=[True, False])
def binary_hash(request: FixtureRequest) -> bool:
    return request.param


@pytest.fixture(
    params=[None, hashlib.md5().name, hashlib.sha1().name, hashlib.sha512().name]
)
def hash_type(request: FixtureRequest) -> Optional[str]:
    return request.param
