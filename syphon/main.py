"""syphon.main.py

   Copyright (c) 2017-2018 Keithley Instruments, LLC.
   Licensed under MIT (https://github.com/ehall/syphon/blob/master/LICENSE)

"""
from os import path
from os import mkdir
from sys import stderr

from .common import ArchiveNotFoundError
from .common import Metadata
from .common import ReadError
from .common import Settings
from .common import SourceFileNotFoundError
from .common import WriteError
from .management import ArchiveEngine
from .management import ColumnExistsError
from .management import CopyError
from .management import CopyValidationError
from .management import CacheEngine
from .verification import verify

from .getparser import get_parser
from .getdataextension import get_data_extension
from .getdatafiles import get_data_files
from .promptbuildversion import prompt_build_version
from .promptdate import prompt_date
from .promptreleaseversion import prompt_release_version
from .promptswitch import prompt_switch
from .purge import purge
from .rebuild import rebuild

def syphon(root: str, argv: list) -> int:
    """Main entry point. Parse arguments, manage import pipelines.

    Args:
        root (str): Highest level of the program directory.
        argv (list): Runtime parameters

    Returns:
        int: An integer exit code. `0` for success or `1` for failure.
    """
    # get populated argument parser
    parser = get_parser()

    # parse input arguments
    args = parser.parse_args(argv[1:])

    try:
        current_settings = None
        # if settings parameter was not specified
        if not getattr(args, 'settings'):
            # get default settings
            current_settings = Settings(path.join(root, 'settings.json'))
        # else if specified settings file path does not exist then complain and quit
        elif not path.exists(args.settings):
            print('Unable to locate settings file: {}'.format(args.settings), file=stderr)
            return 1
        # settings parameter was specified and specified file does exist
        else:
            current_settings = Settings(path.abspath(args.settings))

        # if no arguments
        if len(argv) == 1:
            parser.print_usage()
            return 0
        elif args.version:
            print(current_settings.version)
            return 0
        elif hasattr(args, 'rebuild'):
            # do rebuild
            rebuild(root, current_settings, (args.quiet < 2))

            return 0
        elif hasattr(args, 'switch'):
            # do archive switch
            if getattr(args, 'dir'):
                current_settings.archive_dir = args.dir
            else:
                new_dir = prompt_switch(root, current_settings)
                if new_dir != '':
                    current_settings.archive_dir = new_dir
                    current_settings.save()
                    print('Saved new archive directory')
            return 0

        # ensure archive directory exists
        if not path.exists(path.join(root, current_settings.archive_dir)):
            mkdir(path.join(root, current_settings.archive_dir))

        # call purge and exit if purge subcommand was issued
        if purge(args, current_settings):
            return 0

        data_ext = None
        if len(args.data) == 1:
            # handle mass imports if args.data is a directory
            if path.isdir(args.data[0]):
                data_ext = get_data_extension(args.data[0],
                                              current_settings.metadata_extension
                                             )

        # if not None, then treat args.data as a directory
        if data_ext:
            datafile_list = get_data_files(args.data[0], data_ext)
        else:
            datafile_list = args.data

        for filename in datafile_list:
            # set args.data to new datafile
            args.data = filename

            # if we're not trying to be quiet quiet
            if args.quiet < 2:
                print('\nTargeting {}'.format(args.data))

            current_metadata = None
            metafile = None
            # if the metadata argument wasn't given
            if not getattr(args, 'meta'):
                # if we're trying to be anything above and including quiet,
                # then infer the metadata file
                if args.quiet >= 1:
                    # don't need to check if args.data exists because the parser did that already
                    dataname, _ = path.splitext(path.abspath(args.data))
                    # determine default metadata file
                    metafile = str('{}{}'.format(dataname, current_settings.metadata_extension))
                    # get metadata from specified file
                    current_metadata = Metadata(current_settings, metafile=metafile)
                else:
                    # create empty metadata
                    current_metadata = Metadata(current_settings)

                    # prompt for archive directory
                    new_dir = prompt_switch(root, current_settings)
                    if new_dir != '':
                        current_settings.archive_dir = new_dir
                        current_settings.save()
                        print('  Saved new archive directory')

                    # prompt for release version
                    current_metadata.required['release_version'] = prompt_release_version()

                    # prompt for build version
                    current_metadata.required['build_version'] = prompt_build_version()

                    # prompt for date
                    current_metadata.required['date'] = prompt_date()

                    # newline
                    print()
            else:
                # if it was given, then use it
                metafile = args.meta
                current_metadata = Metadata(current_settings, metafile=metafile)

            # call verification function
            verified, message = verify(current_metadata, current_settings)

            # complain and quit if there are errors
            if not verified:
                print(message)
                return 1


            print(' Verification complete')

            # if we've made it this far, then the data is good enough to import
            archive_engine = ArchiveEngine(path.abspath(args.data),
                                           root,
                                           current_metadata,
                                           current_settings
                                          )
            archive_engine.archive()

            print(' Archival complete')

            # prep data for caching
            cache_engine = CacheEngine(path.join(root, current_settings.data_cache),
                                       archive_engine.data_import_target,
                                       archive_engine.metadata_import_target
                                      )
            flattened_import_data = cache_engine.flatten_file_pair()

            # cache data (data and metadata combined)
            cache_engine.cache_import_data(flattened_import_data)

            print(' Import complete')

        print('\nTotal imports: {}'.format(len(datafile_list) * 2))

    except ArchiveNotFoundError as err:
        print(err.message)
        return 1

    except ColumnExistsError as err:
        print(err.message)
        return 1

    except CopyError as err:
        print(err.message)
        return 1

    except CopyValidationError as err:
        print(err.message)
        return 1

    except KeyboardInterrupt as err:
        print('\nGoodbye')
        return 0

    except ReadError as err:
        print(err.message)
        return 1

    except SourceFileNotFoundError as err:
        print(err.message)
        return 1

    except WriteError as err:
        print(err.message)
        return 1

    except:
        raise
