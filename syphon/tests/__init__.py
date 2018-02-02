"""syphon.tests.__init__.py

   Copyright (c) 2017-2018 Keithley Instruments, LLC.
   Licensed under MIT (https://github.com/ehall/syphon/blob/master/LICENSE)

"""

def get_data_path() -> str:
    """Return an absolute path to the dataset directory.

    Returns:
        str: Absolute path to the data directory.
    """
    from os.path import abspath, dirname, join

    return join(abspath(dirname(__file__)), 'data')
