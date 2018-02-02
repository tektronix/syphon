"""syphon.tests.conftest.py

   Copyright (c) 2017-2018 Keithley Instruments, LLC.
   Licensed under MIT (https://github.com/ehall/syphon/blob/master/LICENSE)

"""
import pytest

from . import get_data_path

@pytest.fixture(scope='module', params=['iris', ':?', '.nonexistant'])
def dataset_factory(request, tmpdir_factory):
    """Extract the given dataset to a temporary directory."""

    def open_dataset(name: str, extract_path: str):
        """Unzip the given dataset environment (stored in `syphon.tests.data`).
        
        Args:
            name (str): Basename of the target archive.
            extract_path (str): Target extraction location.
        """
        from os.path import exists, join
        from shutil import rmtree
        from zipfile import ZipFile

        dataset = join(get_data_path(), '{}.zip'.format(name))

        if not exists(dataset):
            return

        with ZipFile(dataset) as datazip:
            datazip.extractall(path=extract_path)

    target_dir = None
    try:
        target_dir = tmpdir_factory.mktemp(request.param)
        open_dataset(request.param, str(target_dir))
    except:
        pass

    if not target_dir:
        from os.path import dirname, join
        try:
            target_dir = tmpdir_factory.mktemp('invalid')
            target_dir = join(dirname(target_dir), request.param)
        except:
            raise

    return target_dir

@pytest.fixture(scope='function', params=['.meta', '.csv', '.nonexistant'])
def extension_fixture(request):
    return request.param
