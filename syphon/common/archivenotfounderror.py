"""syphon.common.archivenotfounderror.py

   Copyright (c) 2017-2018 Keithley Instruments, LLC.
   Licensed under MIT (https://github.com/ehall/syphon/blob/master/LICENSE)

"""
class ArchiveNotFoundError(Exception):
    """The archive directory cannot be found.

    Args:
        message (str): A meaningful error description.
    """
    def __init__(self, message: str):
        self._message = message
        super(ArchiveNotFoundError, self).__init__(message)

    @property
    def message(self) -> str:
        """Return a string representing the error message."""
        return self._message
