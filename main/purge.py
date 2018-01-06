"""main.purge.py

   Copyright (c) 2017-2018 Keithley Instruments, LLC.
   Licensed under MIT (https://github.com/ehall/syphon/blob/master/LICENSE)

"""
from argparse import Namespace

from common.settings import Settings

def purge(args: Namespace, settings: Settings) -> bool:
    """Handle the `purge` subcommand.

    Note:
        This operation cannot be undone.

    Args:
        args (Namespace): Parsed arguments.
        settings (Settings): Current settings container.

    Returns:
        bool: `True` if the purge subcommand has been issued and the application should exit,
            `False` otherwise.
    """
    if hasattr(args, 'confidence'):
        if args.confidence == 'iknowwhatimdoing':
            assured = None
            if args.quiet < 1:
                assured = input('This will delete EVERYTHING. Are you 100% sure? (yes|No) ')
            else:
                assured = 'yes'

            if assured.lower() == 'yes':
                if args.archives:
                    from management import purge_archives
                    purge_archives(settings.archive_dir)
                    print(' Archives purged')

                if args.cache:
                    from management import purge_cache
                    purge_cache(settings.data_cache)
                    print(' Cache purged')

                print('Purge complete')
            else:
                print('Purge stopped')

        return True
    return False
