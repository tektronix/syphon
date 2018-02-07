"""syphon.init.init.py

   Copyright (c) 2017-2018 Keithley Instruments, LLC.
   Licensed under MIT (https://github.com/ehall/syphon/blob/master/LICENSE)

"""
from syphon.common import Context

def init(context: Context) -> int:
    """Create a schema file in the given directory

    Args:
        context (Context): Runtime settings object.
    
    Returns:
        int: An integer exit code. `0` for success or `1` for failure.

    Raises:
        OSError: File operation error. Error type raised may be a subclass
            of `OSError`.
    """
    from os.path import join
    from syphon.schema import save

    schema_path = join(context.archive, context.schema_file)
    try:
        save(context.schema, schema_path, context.overwrite)
    except:
        raise
    else:
        return 0
