"""syphon.management.purge.py

   Copyright (c) 2017-2018 Keithley Instruments, LLC.
   Licensed under MIT (https://github.com/ehall/syphon/blob/master/LICENSE)

"""
def purge_archives(archive_dir: str) -> list:
    """Delete all archives.

    Args:
        archive_dir (str): Directory location of historic data storage.

    Returns:
        list: An integer list containing deletion statistics.

        The returned list contains the number of files deleted, followed by the
        number of folders deleted.

    Raises:
        OSError: Invalid or inaccessible filename, path, or other argument that is not accepted by
            the operating system.
        PermissionError: File is being used by another process.
    """
    import os
    import shutil

    file_count = 0
    dir_count = 0
    for somefile in os.listdir(archive_dir):
        filepath = os.path.join(archive_dir, somefile)
        if os.path.isfile(filepath):
            file_count += 1
            os.remove(filepath)
        elif os.path.isdir(filepath):
            dir_count += 1
            shutil.rmtree(filepath)

    return [file_count, dir_count]

def purge_cache(master_data_file: str):
    """Delete the data cache.

    Args:
        master_data_file (str): The cache file path.

    Raises:
        OSError: Invalid or inaccessible filename, path, or other argument that is not accepted by
            the operating system.
        PermissionError: Given file is a directory.
    """
    from os.path import exists
    from os import remove

    if exists(master_data_file):
        remove(master_data_file)

    return

def purge_file(archive_file: str) -> (bool, str):
    """Delete the given file.

    Args:
        archive_file (str): File path of file to delete.

    Returns:
        (`bool`, `str`): `False` when file could not be deleted, otherwise `True`. Contains an
            error message when `bool` is `False`, otherwise an empty string.
    """
    from os.path import exists
    from os import remove

    message = ''

    try:
        if exists(archive_file):
            remove(archive_file)

        return (True, message)

    except OSError as err:
        message = err

    except NotImplementedError as err:
        message = err

    except Exception as err:
        message = err

    return (False, message)
