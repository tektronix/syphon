"""syphon.init.init.py

   Copyright Keithley Instruments, LLC.
   Licensed under MIT (https://github.com/tektronix/syphon/blob/master/LICENSE)

"""
from syphon import Context


def init(context: Context):
    """Create a schema file in the given directory

    Args:
        context (Context): Runtime settings object.

    Raises:
        AssertionError: Context.archive is None.
        OSError: File operation error. Error type raised may be
            a subclass of OSError.
    """
    from os.path import join
    from syphon.schema import save

    if context.archive is None:
        raise AssertionError()
    schema_path: str = join(context.archive, context.schema_file)
    save(context.schema, schema_path, context.overwrite)

    if context.verbose:
        print("Init: wrote {0}".format(schema_path))
