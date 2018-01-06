"""main.rebuild.py

   Copyright (c) 2017-2018 Keithley Instruments, LLC.
   Licensed under MIT (https://github.com/ehall/syphon/blob/master/LICENSE)

"""
from common.settings import Settings

def rebuild(root: str, settings: Settings, verbose: bool):
    """Handle the `rebuild` subcommand.

    Args:
        root (str): Highest level of the program directory.
        settings (Settings): Current settings container.
        verbose (bool): Report progress if `True`, otherwise remain silent.
    """
    from os import remove
    from os.path import exists
    from os.path import join
    from os.path import normpath

    from management.cacheengine import CacheEngine

    # get the absolute path to the archive directory
    archive_dir = normpath(join(root, settings.archive_dir))
    # get the metadata file extension
    metadata_file_ext = settings.metadata_extension
    # get the absolute path to the data cache file
    master_data_file = normpath(join(root, settings.data_cache))

    # check if the data cache exists
    if exists(master_data_file):
        if verbose:
            print('Deleting existing data cache @ {}'.format(master_data_file))

        # try to remove the existing cache to prevent rebuild from appending
        try:
            remove(master_data_file)
        except:
            raise

        if verbose:
            print('Cache deleted\n')

    if verbose:
        print('Rebuilding archive @ {}'.format(settings.archive_dir))

    CacheEngine.rebuild_data_cache(archive_dir, metadata_file_ext, master_data_file, verbose)

    if verbose:
        print('Rebuild complete')
