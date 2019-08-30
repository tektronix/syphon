"""syphon.__main__.py

   Copyright Keithley Instruments, LLC.
   Licensed under MIT (https://github.com/tektronix/syphon/blob/master/LICENSE)

"""
from sys import argv
from typing import List, Optional


def bootstrap(args: Optional[List[str]] = None):
    """Main entry point facade."""
    try:
        exit(_main(argv if args is None else args))
    except KeyboardInterrupt:
        raise SystemExit(2)


def _main(args: List[str]) -> int:
    """Main entry point.

    Returns:
        int: An integer exit code. `0` for success or `1` for failure.
    """
    from os.path import abspath, join
    from sortedcontainers import SortedDict
    from typing import Any

    from argparse import ArgumentParser

    from syphon.archive import archive
    from syphon.build_ import build
    from syphon.init import init
    from syphon.schema import load

    from . import Context, get_parser, __version__

    parser: ArgumentParser = get_parser()

    if len(args) <= 1:
        parser.print_usage()
        return 0

    parsed_args: Any = parser.parse_args(args[1:])

    if parsed_args.help is True:
        parser.print_help()
        return 0

    if parsed_args.version is True:
        print(__version__)
        return 0

    this_context = Context()

    this_context.overwrite = parsed_args.force
    this_context.verbose = parsed_args.verbose

    if getattr(parsed_args, "data", False):
        this_context.data = abspath(parsed_args.data)

    if getattr(parsed_args, "destination", False):
        if getattr(parsed_args, "build", False):
            this_context.cache = abspath(parsed_args.destination)
        else:
            this_context.archive = abspath(parsed_args.destination)

    if getattr(parsed_args, "headers", False):
        this_context.schema = SortedDict()
        index = 0
        for header in parsed_args.headers:
            this_context.schema["{}".format(index)] = header
            index += 1

    if getattr(parsed_args, "source", False):
        this_context.archive = abspath(parsed_args.source)

    if getattr(parsed_args, "metadata", False):
        if parsed_args.metadata is not None:
            this_context.meta = abspath(parsed_args.metadata)

    try:
        if getattr(parsed_args, "archive", False):
            if this_context.archive is None:
                raise AssertionError()
            schemafile = join(this_context.archive, this_context.schema_file)
            this_context.schema = load(schemafile)
            archive(this_context)

        if getattr(parsed_args, "init", False):
            init(this_context)

        if getattr(parsed_args, "build", False):
            build(this_context)
    except OSError as err:
        print(str(err))
        return 1

    return 0


if __name__ == "__main__":
    bootstrap(argv)
