"""syphon.__main__.py

   Copyright (c) 2017-2018 Keithley Instruments, LLC.
   Licensed under MIT (https://github.com/ehall/syphon/blob/master/LICENSE)

"""


def _main(argv: list) -> int:
    """Main entry point.

    Returns:
        int: An integer exit code. `0` for success or `1` for failure.
    """
    from os.path import abspath, join
    from sortedcontainers import SortedDict

    from syphon.archive import archive
    from syphon.build_ import build
    from syphon.init import init
    from syphon.schema import load

    from . import Context, get_parser, __version__

    parser = get_parser()
    args = parser.parse_args(argv[1:])

    this_context = Context()

    if args.version is True:
        print(__version__)
        return 0

    this_context.overwrite = args.force
    this_context.verbose = args.verbose

    if getattr(args, 'data', False):
        this_context.data = abspath(args.data)

    if getattr(args, 'destination', False):
        if getattr(args, 'build', False):
            this_context.cache = abspath(args.destination)
        else:
            this_context.archive = abspath(args.destination)

    if getattr(args, 'headers', False):
        this_context.schema = SortedDict()
        index = 0
        for h in args.headers:
            this_context.schema['{}'.format(index)] = h
            index += 1

    if getattr(args, 'source', False):
        this_context.archive = abspath(args.source)

    if getattr(args, 'metadata', False):
        if args.metadata is not None:
            this_context.meta = abspath(args.metadata)

    try:
        if getattr(args, 'archive', False):
            schemafile = join(this_context.archive, this_context.schema_file)
            this_context.schema = load(schemafile)
            archive(this_context)

        if getattr(args, 'init', False):
            init(this_context)

        if getattr(args, 'build', False):
            build(this_context)
    except OSError as err:
        print(str(err))
        return 1

    return 0


if __name__ == '__main__':
    from sys import argv

    exit(_main(argv))
