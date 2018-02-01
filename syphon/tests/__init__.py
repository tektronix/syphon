"""syphon.tests.__init__.py

   Copyright (c) 2017-2018 Keithley Instruments, LLC.
   Licensed under MIT (https://github.com/ehall/syphon/blob/master/LICENSE)

"""

def close_dataset(name: str):
    """Delete the directory of the given dataset environment.

    Args:
        name (str): Directory to delete.
    """
    from os.path import join
    from shutil import rmtree

    dataset = join(get_data_path(), name)
    rmtree(dataset)

def close_all_datasets():
    """Delete all open dataset environments."""
    from os import walk
    from shutil import rmtree

    for root, dirs, _ in walk(get_data_path()):
        for dirname in dirs:
            rmtree(path.join(root, dirname))
        break

def get_data_path() -> str:
    """Return an absolute path to the dataset directory.

    Returns:
        str: Absolute path to the data directory.
    """
    from os.path import abspath, dirname, join

    return join(abspath(dirname(__file__)), 'data')

def open_dataset(name: str):
    """Unzip the given dataset environment in `syphon.tests.data`.

    Args:
        name (str): Basename of a dataset zip archive.

    Raises:
        FileNotFoundError: Given dataset archive cannot be found.
    """
    from os.path import join
    from zipfile import ZipFile

    dataset = join(get_data_path(), '{}.zip'.format(name))
    with ZipFile(dataset) as datazip:
        datazip.extractall()
