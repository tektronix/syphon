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

    @staticmethod
    def generate_message(process: str, location: str) -> str:
        """Return a generated message string.

        Args:
            process (str): Name of the process which will raise the `ArchiveNotFoundError`.
            location (str): The expected location of the archive directory.
        """
        capital_process = process.capitalize()
        return '{} error. Unable to locate archive directory {}'.format(capital_process,
                                                                        location
                                                                       )
