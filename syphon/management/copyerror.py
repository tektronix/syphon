"""syphon.management.copyerror.py

   Copyright (c) 2017-2018 Keithley Instruments, LLC.
   Licensed under MIT (https://github.com/ehall/syphon/blob/master/LICENSE)

"""
class CopyError(Exception):
    """Error during copy operation.

    Args:
      message (str): A meaningful error description.
    """
    def __init__(self, message: str):
        self._message = message
        super(CopyError, self).__init__(message)

    @property
    def message(self) -> str:
        """Return a string representing the error message."""
        return self._message
