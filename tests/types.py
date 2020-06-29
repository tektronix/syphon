"""tests.types.py

   Copyright Keithley Instruments, LLC.
   Licensed under MIT (https://github.com/tektronix/syphon/blob/master/LICENSE)

"""
from enum import Enum, auto, unique


@unique
class PathType(Enum):
    ABSOLUTE = auto()
    RELATIVE = auto()
    NONE = auto()  # Only the filename.
