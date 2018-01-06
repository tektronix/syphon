"""main.getparser.py

   Copyright (c) 2017-2018 Keithley Instruments, LLC.
   Licensed under MIT (https://github.com/ehall/syphon/blob/master/LICENSE)

"""
import argparse

def get_parser() -> argparse.ArgumentParser:
    """Return `ArgumentParser` used to parse `syphon` arguments."""
    # create parser with the given arguments
    # conflict_handler='resolve' -- allows parser to have keyword specific help
    # formatter_class=RawDescriptionHelpFormatter -- format descriptions before output
    parser = argparse.ArgumentParser(conflict_handler='resolve',
                                     description='A data storage and management engine.',
                                     formatter_class=argparse.RawDescriptionHelpFormatter
                                    )
    # -q  -- hide prompts
    # -qq -- hide prompts and output
    parser.add_argument('-q',
                        '--quiet',
                        action='count',
                        default=0,
                        help='hide import prompts and decrease output verbosity',
                        required=False
                       )
    # path to settings file or None if omitted
    parser.add_argument('--settings',
                        default=None,
                        help='alternate settings file',
                        required=False
                       )
    # version information
    parser.add_argument('--version',
                        action='store_true',
                        default=False,
                        help='display version information',
                        required=False
                       )
    # multiline string for the subcommand description.
    # %(prog)s -- replaced with the name of the program
    subparser_description = ('Additional subcommand help is available via\n'
                             '      %(prog)s subcommand (-h|--help)'
                            )
    # parserception: create a subparser group within the original parser
    subparsers = parser.add_subparsers(description=subparser_description, title='subcommands')

    # create archive backup

    # import command
    # create import subcommand parser
    import_parser = subparsers.add_parser('import', help='import data file and cache its contents')
    # create positional argument group
    positional_group = import_parser.add_argument_group('positional arguments')
    # required data file
    positional_group.add_argument('--data',
                                  help='data file to import',
                                  nargs='+'
                                 )
    # optional metadata file
    positional_group.add_argument('--meta',
                                  default=None,
                                  help='metadata for the specified data file',
                                  nargs='?'
                                 )

    # purge command
    # create purge subcommand parser
    purge_parser = subparsers.add_parser('purge', help='delete archived data files')
    purge_parser.add_argument('--archives',
                              action='store_true',
                              default=False,
                              help='permanently delete all files from the archive'
                             )
    purge_parser.add_argument('--cache',
                              action='store_true',
                              default=False,
                              help='permanently delete the data cache'
                             )
    purge_parser.add_argument('confidence', choices=['iknowwhatimdoing'])

    # rebuild command
    # create rebuild subcommand parser
    rebuild_parser = subparsers.add_parser('rebuild', help='create cache from archived data files')
    # create optional, hidden argument that is always true when the rebuild subcommand is passed
    rebuild_parser.add_argument('--rebuild',
                                action='store_true',
                                default=True,
                                help=argparse.SUPPRESS,
                                required=False
                               )

    # switch command
    # create switch subcommand parser
    switch_parser = subparsers.add_parser('switch', help='change the archive directory')
    # create optional, hidden argument that is always true when the switch subcommand is passed
    switch_parser.add_argument('--switch',
                               action='store_true',
                               default=True,
                               help=argparse.SUPPRESS,
                               required=False
                              )
    # optional directory name
    switch_parser.add_argument('dir',
                               default=None,
                               help='name of the new archive directory',
                               nargs='?'
                              )

    return parser
