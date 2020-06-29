"""syphon._cmdparser.py

   Copyright Keithley Instruments, LLC.
   Licensed under MIT (https://github.com/tektronix/syphon/blob/master/LICENSE)

"""
import argparse


def get_parser() -> argparse.ArgumentParser:
    """Return `ArgumentParser` used to parse `syphon` arguments."""
    from . import __url__
    from .core.check import DEFAULT_FILE as DEFAULT_HASH_FILE

    epilog_last_line = "Syphon home page: <{}>".format(__url__)
    hashfile_epilog = "\n".join(
        [
            "If left unspecified, the HASHFILE defaults to a file named",
            '"%s" located beside a built file.' % DEFAULT_HASH_FILE,
            "",
            "Entries in a valid HASHFILE must be in the same format used by",
            "the GNU coreutils sha256sum command. That is, each entry takes",
            "the form of",
            "\tCHECKSUM [*| ]FILEPATH",
            'Where CHECKSUM is the computed message digest, "*" or " " (a',
            "space character) indicates the read mode of binary or text",
            "respectively, and FILEPATH is the hashed file.",
            "Relative FILEPATHs are always relative to the calling directory.",
            "Every entry in a HASHFILE is assumed to have been calculated",
            "with the SHA256 hashing function.",
            "",
            epilog_last_line,
        ]
    )

    # create parser with the given arguments
    # conflict_handler='resolve' -- allows parser to have keyword
    #   specific help
    # formatter_class=RawDescriptionHelpFormatter -- format descriptions
    #   before output
    parser = argparse.ArgumentParser(
        add_help=False,
        conflict_handler="resolve",
        description="A data storage and management engine.",
        epilog=epilog_last_line,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        prog=__package__,
    )
    # force overwrite
    parser.add_argument(
        "-f",
        "--force",
        action="store_true",
        default=False,
        help="overwrite existing files",
        required=False,
    )
    # help
    parser.add_argument(
        "-h",
        "--help",
        action="store_true",
        default=False,
        help="display this help and exit",
        required=False,
    )
    # verbosity
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        default=False,
        help="explain what is being done",
        required=False,
    )
    # version information
    parser.add_argument(
        "--version",
        action="store_true",
        default=False,
        help="output version information and exit",
        required=False,
    )

    # multiline string for the subcommand description.
    # %(prog)s -- replaced with the name of the program
    subparser_description = (
        "Additional subcommand help is available via\n"
        "      %(prog)s subcommand (-h|--help)"
    )
    # create a subparser group within the original parser
    subparsers = parser.add_subparsers(
        description=subparser_description, title="subcommands"
    )

    # archive command
    # create archive subcommand parser
    archive_parser = subparsers.add_parser(
        "archive",
        epilog=hashfile_epilog,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        help="import files into the archive directory",
    )
    # optional, hidden argument that is true when using this subparser
    # but does not exist otherwise
    archive_parser.add_argument(
        "--archive",
        action="store_true",
        default=True,
        help=argparse.SUPPRESS,
        required=False,
    )
    archive_parser.add_argument(
        "archive_source", help="file or glob pattern", metavar="SOURCE", nargs="+"
    )
    archive_parser.add_argument(
        "archive_destination",
        help="directory where data is stored",
        metavar="DESTINATION",
    )
    archive_parser.add_argument(
        "-m",
        "--meta-mask",
        default=None,
        dest="meta_mask",
        help=(
            "string pattern that indicates a metadata file when contained in a source "
            "filepath"
        ),
        metavar="MASK",
        nargs="+",
        required=False,
        type=str,
    )
    archive_parser.add_argument(
        "-s",
        "--schema",
        default=None,
        help="a JSON file containing the archive storage schema",
        metavar="SCHEMAFILE",
        required=False,
        type=str,
    )
    # Filemap behavior arguments.
    behavior_group = archive_parser.add_argument_group(
        "mapping behavior arguments",
        "Mutually exclusive optional arguments that control file mapping.",
    )
    behavior_exclusive_group = behavior_group.add_mutually_exclusive_group(
        required=False
    )
    behavior_exclusive_group.add_argument(
        "--one-to-one",
        action="store_true",
        default=True,
        dest="one_to_one",
        help=(
            "pairs a data filename, excluding extension, to a metadata file with the "
            "same name (the default)"
        ),
        required=False,
    )
    behavior_exclusive_group.add_argument(
        "--one-to-many",
        action="store_true",
        default=False,
        dest="one_to_many",
        help="associates each data file to every available metadata file",
        required=False,
    )
    # Incremental build arguments.
    incremental_build_group = archive_parser.add_argument_group(
        "incremental build arguments",
        (
            "Optional arguments to perform an incremental build after archival.\n"
            "HASHFILE cannot be specified without a BUILDFILE."
        ),
    )
    incremental_build_group.add_argument(
        "-i",
        "--increment",
        default=None,
        help="build file to update with newly archived files",
        metavar="BUILDFILE",
        required=False,
        type=str,
    )
    incremental_build_group.add_argument(
        "--hashfile",
        default=None,
        dest="increment_hashfile",
        help="an optional file to use for the BUILDFILE integrity check",
        metavar="HASHFILE",
        required=False,
        type=str,
    )

    # build command
    # create build subcommand parser
    build_parser = subparsers.add_parser(
        "build",
        epilog=hashfile_epilog,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        help="combine archives into a single file",
    )
    # optional, hidden argument that is true when using this subparser
    # but does not exist otherwise
    build_parser.add_argument(
        "--build",
        action="store_true",
        default=True,
        help=argparse.SUPPRESS,
        required=False,
    )
    build_parser.add_argument(
        "build_source", help="directory where data is stored", metavar="SOURCE"
    )
    build_parser.add_argument(
        "build_destination", help="filename of the output file", metavar="DESTINATION"
    )
    build_parser.add_argument(
        "hashfile",
        default=None,
        help="the file to update with a new DESTINATION hash",
        metavar="HASHFILE",
        nargs="?",
    )
    build_parser.add_argument(
        "--no-hash",
        action="store_true",
        default=False,
        dest="build_no_hash",
        help="skip the hashing process",
        required=False,
    )

    # check command
    # create check subcommand parser
    check_parser = subparsers.add_parser(
        "check",
        epilog=hashfile_epilog,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        help="verifies the integrity of a built file",
    )
    # optional, hidden argument that is true when using this subparser
    # but does not exist otherwise
    check_parser.add_argument(
        "--check",
        action="store_true",
        default=True,
        help=argparse.SUPPRESS,
        required=False,
    )
    check_parser.add_argument(
        "check_source", help="file output by the build command", metavar="SOURCE"
    )
    check_parser.add_argument(
        "hashfile",
        default=None,
        help="the file containing the hash entry of the SOURCE file",
        metavar="HASHFILE",
        nargs="?",
    )

    # init command
    # create init subcommand parser
    init_parser = subparsers.add_parser(
        "init",
        epilog=epilog_last_line,
        help="create an archive directory storage schema",
    )
    # optional, hidden argument that is true when using this subparser
    # but does not exist otherwise
    init_parser.add_argument(
        "--init",
        action="store_true",
        default=True,
        help=argparse.SUPPRESS,
        required=False,
    )
    init_parser.add_argument(
        "init_destination", help="directory where data is stored", metavar="DESTINATION"
    )
    init_parser.add_argument(
        "headers",
        help="column header(s) to use for the archive hierarchy",
        metavar="HEADER",
        nargs="+",
    )

    return parser
