#!python3
"""syphon.__init__.py

   Copyright (c) 2017-2018 Keithley Instruments, LLC.
   Licensed under MIT (https://github.com/ehall/syphon/blob/master/LICENSE)

"""
from ._cmdparser import get_parser
from .context import Context
from ._url import get_url
from ._version import get_versions


__url__ = get_url()
del get_url

__version__ = get_versions()['version']
del get_versions

__all__ = [
    'get_parser',
    'Context',
    '__url__',
    '__version__',
]
