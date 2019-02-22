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
        OSError: File operation error. Error type raised may be
            a subclass of OSError.
    """
    from os.path import join
    from syphon.schema import save

    schema_path = join(context.archive, context.schema_file)
    save(context.schema, schema_path, context.overwrite)

    if context.verbose:
        print('Init: wrote {0}'.format(schema_path))
