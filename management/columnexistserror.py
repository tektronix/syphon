"""management.columnexistserror.py

   Copyright (c) 2017-2018 Keithley Instruments, LLC.
   Licensed under MIT (https://github.com/ehall/syphon/blob/master/LICENSE)

"""
class ColumnExistsError(Exception):
    """Raised when a metadata tag and data column label collision occur.

    Args:
        message (str): A meaningful error description.
    """
    def __init__(self, message: str):
        self._message = message
        super(ColumnExistsError, self).__init__(message)

    @property
    def message(self) -> str:
        """Return a string representing the error message."""
        return self._message
