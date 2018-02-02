"""syphon.tests.conftest.py

   Copyright (c) 2017-2018 Keithley Instruments, LLC.
   Licensed under MIT (https://github.com/ehall/syphon/blob/master/LICENSE)

"""
import pytest

from . import get_data_path

# def close_dataset():
#     """Delete the directory of the given dataset environment."""
#     from os.path import join
#     from shutil import rmtree

#     dataset = join(get_data_path(), request.param)
#     rmtree(dataset)

# @pytest.fixture(scope='session')
# def close_all_datasets():
#     """Delete all open dataset environments."""
#     from os import walk
#     from os.path import join
#     from shutil import rmtree

#     for root, dirs, _ in walk(get_data_path()):
#         for dirname in dirs:
#             rmtree(join(root, dirname))
#         break

@pytest.fixture(params=['iris', ':?', '.nonexistant'])
def dataset_factory(tmpdir_factory, request):
    """Extract the given dataset to a temporary directory."""
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
