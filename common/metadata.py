"""common.metadata.py

   Copyright (c) 2017-2018 Keithley Instruments, LLC.
   Licensed under MIT (https://github.com/ehall/syphon/blob/master/LICENSE)

"""
from .readerror import ReadError
from .settings import Settings
from .sourcefilenotfounderror import SourceFileNotFoundError

class Metadata:
    """Contains methods for accessing metadata.

    Omitting the metafile argument creates an empty Metadata class.

    Args:
        settings (Settings): Current settings object.
        metafile (str): Filepath of the metadata file. Defaults to None.

    Raises:
        ReadError: An error occurred during the read operation.
        SourceFileNotFoundError: Data or metadata file cannot be found.
    """
    def __init__(self, settings: Settings, metafile=str()):
        from numpy import nan
        from pandas import DataFrame
        from pandas import read_csv
        from os import path

        self._common = {}
        self._required = {}

        if not metafile:
            return

        if not path.exists(metafile):
            message = SourceFileNotFoundError.generate_message('Metadata', metafile)
            raise SourceFileNotFoundError(message)

        # import metadata
        metadata = DataFrame()
        try:
            metadata = DataFrame(read_csv(metafile, dtype=str))
        except Exception as err:
            raise ReadError(err)

        # remove any 'Unnamed' columns
        metadata.dropna(axis=1, how='all', inplace=True)

        # get required tags
        required_tags = settings.required_tags

        # find all required tags and store them and their values
        self._required = {}
        for tag in required_tags:
            if metadata.get(tag) is not None:
                value = metadata.get(tag).get(0)
                if value is not nan:
                    self._required[tag] = value
                    # remove the column since we're done with it
                    metadata.drop(tag, axis=1, inplace=True)
                else:
                    pass    # complain in verification
            else:
                pass    # complain in verification

        # find all remaining tags and store them and their values
        self._common = {}
        for column_header in metadata.columns:
            value = metadata.get(column_header).get(0)
            if value is not nan:
                self._common[column_header] = value

    @property
    def common(self) -> dict:
        """`dict`: All non-required metadata tags and values."""
        return self._common

    @common.setter
    def common(self, key, value):
        self._common[key] = value

    @property
    def required(self) -> dict:
        """`dict`: Required metadata tags and values."""
        return self._required

    @required.setter
    def required(self, key, value):
        self._required[key] = value
