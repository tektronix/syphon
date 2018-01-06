"""massimport.getdatafiles.py

   Copyright (c) 2017-2018 Keithley Instruments, LLC.
   Licensed under MIT (https://github.com/ehall/syphon/blob/master/LICENSE)

"""
def get_data_files(directory: str, data_extension: str) -> list:
    """Return a list of strings representing all files in the given directory
    with the probable data extension.

    Args:
        directory (str): Location to start extension search.
        data_extension (str): The data file extension.

    Returns:
        list: A list of files with the data extension.
    """
    from glob import glob
    from os import path

    # get known file name
    return glob(path.join(directory, '*{}'.format(data_extension)))
