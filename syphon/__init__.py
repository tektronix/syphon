# flake8: noqa
"""syphon.__init__.py

   Copyright Keithley Instruments, LLC.
   Licensed under MIT (https://github.com/tektronix/syphon/blob/master/LICENSE)

"""
from . import _version
from .core.archive.archive import archive
from .core.build import build
from .core.check import check
from .core.init import init

__url__ = "https://github.com/tektronix/syphon"

__version__ = _version.get_versions()["version"]
del _version

__all__ = ["archive", "build", "check", "init", "__url__", "__version__"]
