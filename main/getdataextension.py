"""massimport.getdataextension.py

   Copyright (c) 2017-2018 Keithley Instruments, LLC.
   Licensed under MIT (https://github.com/ehall/syphon/blob/master/LICENSE)

"""
def get_data_extension(directory: str, meta_extension: str) -> str:
    """Return a string representing a probable data extension of a given
    directory or `None` if no metadata files could be found.

    Args:
        directory (str): Location to start extension search.
        meta_extension (str): The metadata file extension.

    Returns:
        str: The probable data extension. `None` if no metadata files were found.
    """
    from glob import glob
    from os import path

    if directory[-1] != '\\' or directory[-1] != '/':
        directory = '{}/'.format(directory)

    # get known file name
    metafile = None
    for item in glob(path.join(directory, '*{}'.format(meta_extension))):
        metafile = item
        break
    else:
        return

    # splitext will return everything before the last period (.) including path
    filename_and_path, _ = path.splitext(metafile)

    # search target
    glob_target = '{}.{}'.format(filename_and_path, '*')

    # get all files with the specified filename
    files = glob(glob_target)

    for somefile in files:
        _, some_ext = path.splitext(somefile)
        # find first file that does not have the metadata extension
        if not meta_extension in some_ext:
            return some_ext
