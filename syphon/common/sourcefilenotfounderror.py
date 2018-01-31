"""syphon.common.sourcefilenotfounderror.py

   Copyright (c) 2017-2018 Keithley Instruments, LLC.
   Licensed under MIT (https://github.com/ehall/syphon/blob/master/LICENSE)

"""
class SourceFileNotFoundError(Exception):
    """Data or metadata file cannot be found.

    Args:
        message (str): A meaningful error description.
    """
    def __init__(self, message: str):
        self._message = message
        super(SourceFileNotFoundError, self).__init__(message)

    @property
    def message(self) -> str:
        """Return a string representing the error message."""
        return self._message

    @staticmethod
    def generate_message(process: str, location: str) -> str:
        """Return a generated message string.

        Args:
            process (str): Name of the process which will raise the `SourceFileNotFoundError`.
            location (str): The expected location of the source file.
        """
        capital_process = process.capitalize()
        return '{} error. Unable to locate source file: {}'.format(capital_process,
                                                                   location
                                                                  )
