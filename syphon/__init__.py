# flake8: noqa
"""syphon.__init__.py

   Copyright Keithley Instruments, LLC.
   Licensed under MIT (https://github.com/tektronix/syphon/blob/master/LICENSE)

"""
from ._cmdparser import get_parser
from .context import Context


__url__ = 'https://github.com/tektronix/syphon'

__all__ = [
    'get_parser',
    'Context',
    '__url__',
    '__version__',
]

from ._version import get_versions
__version__ = get_versions()['version']
del get_versions
