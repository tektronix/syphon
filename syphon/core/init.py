"""syphon.core.init.py

   Copyright Keithley Instruments, LLC.
   Licensed under MIT (https://github.com/tektronix/syphon/blob/master/LICENSE)

"""
from sortedcontainers import SortedDict


def init(
    new_schema: SortedDict,
    schema_filepath: str,
    overwrite: bool = False,
    verbose: bool = False,
):
    """Create a schema file in the given directory.

    Args:
        new_schema: The desired storage schema.
        schema_filepath: Absolute path to a JSON file containing a storage schema.
        overwrite: Whether an existing schema file should be replaced.
        verbose: Whether activities should be printed to the standard output.

    Raises:
        OSError: File operation error. Error type raised may be
            a subclass of OSError.
    """
    from syphon import schema

    schema.save(new_schema, schema_filepath, overwrite)

    if verbose:
        print("Init: wrote {0}".format(schema_filepath))
