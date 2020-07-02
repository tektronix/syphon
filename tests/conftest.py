"""tests.conftest.py

   Copyright Keithley Instruments, LLC.
   Licensed under MIT (https://github.com/tektronix/syphon/blob/master/LICENSE)

"""
import random
from typing import Dict, List, Optional

import pytest
from _pytest.config import Config
from _pytest.config.argparsing import Parser
from _pytest.fixtures import FixtureRequest
from _pytest.nodes import Item
from pandas.util.testing import makeCustomIndex
from py._path.local import LocalPath

from . import rand_string
from .types import PathType

MAX_DATA_FILES = 4
MAX_METADATA_COLS = 5
MAX_VALUES_PER_META_COL = 3


def pytest_addoption(parser: Parser):
    parser.addoption(
        "--slow", action="store_true", default=False, help="Run slow tests."
    )


def pytest_configure(config: Config):
    import os

    if config.option.help:
        return

    if "PYTHONHASHSEED" not in os.environ:
        print("PYTHONHASHSEED environment variable not provided. Rolling manually...")
        os.environ["PYTHONHASHSEED"] = str(random.randint(0, 1000))
        print(f"PYTHONHASHSEED={os.environ['PYTHONHASHSEED']}")

    random.seed(a=int(os.environ["PYTHONHASHSEED"]))


def pytest_collection_modifyitems(config: Config, items: List[Item]):
    if not config.getoption("--slow"):
        for item in items:
            if "slow" in item.keywords:
                item.add_marker(pytest.mark.skip(reason="Need --slow flag to run."))


@pytest.fixture
def archive_dir(tmpdir: LocalPath) -> LocalPath:
    return tmpdir.mkdir("archive")


@pytest.fixture
def cache_file(tmpdir: LocalPath) -> LocalPath:
    return tmpdir.join("cache.csv")


@pytest.fixture
def hash_file(tmpdir: LocalPath) -> LocalPath:
    return tmpdir.join("hash.sums")


@pytest.fixture
def import_dir(tmpdir: LocalPath) -> LocalPath:
    return tmpdir.mkdir("import")


@pytest.fixture(params=[True, False])
def schema_file(request: FixtureRequest, archive_dir: LocalPath) -> Optional[LocalPath]:
    return None if request.param else archive_dir.dirpath("schemafile")


@pytest.fixture(params=[x for x in range(0, MAX_METADATA_COLS)])
def metadata_column_headers(request: FixtureRequest) -> List[str]:
    """Make a list of metadata column headers.

    Returns:
        list: A metadata column header list whose length is between 0
            and `MAX_METADATA_COLS`.
    """
    if request.param == 0:
        return list()
    # pandas bug (?) in makeCustomIndex when nentries = 1
    elif request.param == 1:
        return ["M_l0_g0"]
    else:
        return list(makeCustomIndex(request.param, 1, prefix="M"))


@pytest.fixture(params=[x for x in range(0, MAX_VALUES_PER_META_COL + 1)])
def metadata_columns(
    request: FixtureRequest, metadata_column_headers: List[str]
) -> Dict[str, List[str]]:
    """Make a metadata column header and column value dictionary."""
    columns: Dict[str, List[str]] = {}
    for header in metadata_column_headers:
        columns[header] = []
        for i in range(0, request.param):
            columns[header].append(f"val{i}")
    return columns


@pytest.fixture
def metadata_random_columns(metadata_column_headers: List[str]) -> Dict[str, List[str]]:
    """Make dictionary containing lists between 1 and
    `MAX_VALUES_PER_META_COL` in length."""

    def _rand_depth(max_: int):
        return random.randint(1, max_)

    columns: Dict[str, List[str]] = {}
    for header in metadata_column_headers:
        columns[header] = []
        for i in range(0, _rand_depth(MAX_VALUES_PER_META_COL)):
            columns[header].append(f"val{i}")
    return columns


@pytest.fixture(params=[x for x in range(1, MAX_DATA_FILES)])
def random_data(request: FixtureRequest, import_dir: LocalPath) -> List[str]:
    files: List[str] = list()
    for _ in range(request.param):
        files.append(str(import_dir.join(f"{rand_string()}.csv")))
    return files


@pytest.fixture(params=[x for x in range(0, MAX_DATA_FILES * 2)])
def random_metadata(request: FixtureRequest, import_dir: LocalPath) -> List[str]:
    files: List[str] = list()
    for _ in range(request.param):
        files.append(str(import_dir.join(f"{rand_string()}.meta")))
    return files


@pytest.fixture(params=[True, False])
def incremental(request: FixtureRequest) -> bool:
    return request.param


@pytest.fixture(params=[True, False])
def overwrite(request: FixtureRequest) -> bool:
    return request.param


@pytest.fixture(params=[PathType.ABSOLUTE, PathType.RELATIVE, PathType.NONE])
def path_type_cachefile(request: FixtureRequest) -> PathType:
    return request.param


@pytest.fixture(params=[PathType.ABSOLUTE, PathType.RELATIVE, PathType.NONE])
def path_type_hashentry(request: FixtureRequest) -> PathType:
    return request.param


@pytest.fixture(params=[True, False])
def post_hash(request: FixtureRequest) -> bool:
    return request.param


@pytest.fixture(params=[True, False])
def verbose(request: FixtureRequest) -> bool:
    return request.param
