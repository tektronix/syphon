"""syphon._cmdparser.py

   Copyright Keithley Instruments, LLC.
   Licensed under MIT (https://github.com/ehall/syphon/blob/master/LICENSE)

"""
import argparse


def get_parser() -> argparse.ArgumentParser:
    """Return `ArgumentParser` used to parse `syphon` arguments."""
    from . import __url__

    epilog_last_line = 'Syphon home page: <{}>'.format(__url__)

    # create parser with the given arguments
    # conflict_handler='resolve' -- allows parser to have keyword
    #   specific help
    # formatter_class=RawDescriptionHelpFormatter -- format descriptions
    #   before output
    parser = argparse.ArgumentParser(
        add_help=False,
        conflict_handler='resolve',
        description='A data storage and management engine.',
        epilog=epilog_last_line,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        prog=__package__)
    # force overwrite
    parser.add_argument(
        '-f',
        '--force',
        action='store_true',
        default=False,
        help='overwrite existing files',
        required=False)
    # help
    parser.add_argument(
        '-h',
        '--help',
        action='store_true',
        default=False,
        help='display this help and exit',
        required=False)
    # verbosity
    parser.add_argument(
        '-v',
        '--verbose',
        action='store_true',
        default=False,
        help='explain what is being done',
        required=False)
    # version information
    parser.add_argument(
        '--version',
        action='store_true',
        default=False,
        help='output version information and exit',
        required=False)

    # multiline string for the subcommand description.
    # %(prog)s -- replaced with the name of the program
    subparser_description = (
        'Additional subcommand help is available via\n'
        '      %(prog)s subcommand (-h|--help)')
    # parserception: create a subparser group within the original parser
    subparsers = parser.add_subparsers(
        description=subparser_description,
        title='subcommands')

    # archive command
    # create archive subcommand parser
    archive_parser = subparsers.add_parser(
        'archive',
        epilog=epilog_last_line,
        help='import files into the archive directory')
    # optional, hidden argument that is true when using this subparser
    archive_parser.add_argument(
        '--archive',
        action='store_true',
        default=True,
        help=argparse.SUPPRESS,
        required=False)
    # required destination directory
    archive_parser.add_argument(
        'destination',
        help='directory where data is archived')
    # required data file/glob pattern
    archive_parser.add_argument(
        '-d',
        '--data',
        help='data file or glob pattern',
        required=True)
    # optional metadata file/glob pattern
    archive_parser.add_argument(
        '-m',
        '--metadata',
        default=None,
        help='metadata file or glob pattern',
        required=False)

    # build command
    # create build subcommand parser
    build_parser = subparsers.add_parser(
        'build',
        epilog=epilog_last_line,
        help='combine archives into a single file')
    # optional, hidden argument that is true when using this subparser
    build_parser.add_argument(
        '--build',
        action='store_true',
        default=True,
        help=argparse.SUPPRESS,
        required=False)
    # required source directory
    build_parser.add_argument(
        'source',
        help='directory where data is stored')
    # required destination file
    build_parser.add_argument(
        'destination',
        help='filename of the output file')

    # init command
    # create init subcommand parser
    init_parser = subparsers.add_parser(
        'init',
        epilog=epilog_last_line,
        help='create an archive directory storage schema')
    # optional, hidden argument that is true when using this subparser
    init_parser.add_argument(
        '--init',
        action='store_true',
        default=True,
        help=argparse.SUPPRESS,
        required=False)
    # required destination directory
    init_parser.add_argument(
        'destination',
        help='directory where data is archived')
    # required header
    init_parser.add_argument(
        'headers',
        metavar='header',
        help='column header(s) to use for the archive hierarchy',
        nargs='+')

    return parser
