"""syphon.management.archiveengine.py

   Copyright (c) 2017-2018 Keithley Instruments, LLC.
   Licensed under MIT (https://github.com/ehall/syphon/blob/master/LICENSE)

"""
from os import makedirs
from os import path
from shutil import copy2

from syphon.common import ArchiveNotFoundError
from syphon.common import Metadata
from syphon.common import Settings
from syphon.common import SourceFileNotFoundError

from .archivefileexistserror import ArchiveFileExistsError
from .copyerror import CopyError
from .copyvalidationerror import CopyValidationError

class ArchiveEngine:
    """Contains methods for performing data archival.

    Args:
        data_file (str): Filepath of the data file.
        root (str): Highest level of the program directory.
        metadata (Metadata): Current metadata container.
        settings (Settings): Current settings container.

    Raises:
        ArchiveNotFoundError: Archive directory cannot be found.
        SourceFileNotFoundError: Data or metadata file cannot be found.
    """
    def __init__(self,
                 data_file: str,
                 root: str,
                 metadata: Metadata,
                 settings: Settings
                ):
        # ensure everything is valid
        if not path.exists(data_file):
            message = SourceFileNotFoundError.generate_message('Archival', data_file)
            raise SourceFileNotFoundError(message)

        if not path.exists(path.join(root, settings.archive_dir)):
            message = ArchiveNotFoundError.generate_message('Archival', settings.archive_dir)
            raise ArchiveNotFoundError(message)

        # save locations now that we know they're valid
        self._archive_dir = path.join(root, settings.archive_dir)
        self._data_file = data_file

        # save target metadata information
        self._common_tags = metadata.common
        self._required_tags = metadata.required

        # get archive schema
        archive_schema = settings.archive_schema

        # build target directory structure
        target_dir = self._archive_dir
        for key in range(0, len(archive_schema)):
            # get metadata tag for this directory level
            tag = archive_schema.get(str(key))
            # get metadata tag
            value = str(metadata.required.get(tag))
            # make lowercase
            value = value.lower()
            # replace spaces with underscores
            value = value.replace(' ', '_')
            # add to target archive path
            target_dir = path.join(target_dir, value)

        target_file = path.basename(data_file)
        self._target_data_filepath = path.join(target_dir, target_file)
        self._target_data_filepath = path.abspath(self._target_data_filepath)
        target_name, _ = path.splitext(target_file)
        self._target_meta_filepath = path.join(target_dir,
                                               '{}{}'.format(target_name,
                                                             settings.metadata_extension
                                                            ))
        self._target_meta_filepath = path.abspath(self._target_meta_filepath)

    @property
    def data_import_target(self) -> str:
        """Return a string representing the absolute path of the data file once imported."""
        return self._target_data_filepath

    @property
    def metadata_import_target(self) -> str:
        """Return a string representing the absolute path of the metadata file once imported."""
        return self._target_meta_filepath

    def archive(self):
        """Copy data and metadata files to the archive.

        The data, metadata, and archive paths used are those passed to the `ArchiveEngine`
        constructor.

        Raises:
            ArchiveNotFoundError: Archive directory cannot be found.
            CopyError: An error occurred during file copy.
            CopyValidationError: Destination files cannot be found after copying.
            SourceFileNotFoundError: Data or metadata file cannot be found.
        """
        from pandas import concat
        from pandas import DataFrame

        # ensure everything is still valid
        if not path.exists(self._data_file):
            message = SourceFileNotFoundError.generate_message('Archival', self._data_file)
            raise SourceFileNotFoundError(message)

        if not path.exists(self._archive_dir):
            message = ArchiveNotFoundError.generate_message('Archival', self._archive_dir)
            raise ArchiveNotFoundError(message)

        target_data_dir, _ = path.split(self._target_data_filepath)
        target_metadata_dir, _ = path.split(self._target_meta_filepath)

        # check if target data directory exists
        if not path.exists(target_data_dir):
            makedirs(target_data_dir)

        # check if target metadata directory exists
        if not path.exists(target_metadata_dir):
            makedirs(target_metadata_dir)

        # check if the destination files already exist
        if path.isfile(self._target_data_filepath):
            message = ArchiveFileExistsError.generate_message(self._target_data_filepath)
            raise ArchiveFileExistsError(message)
        elif path.isfile(self._target_meta_filepath):
            message = ArchiveFileExistsError.generate_message(self._target_meta_filepath)
            raise ArchiveFileExistsError(message)
        else:
            # create metadata lists
            common_list = list(self._common_tags.items())
            required_list = list(self._required_tags.items())
            # create metadata DataFrame
            metaframe = DataFrame(concat([DataFrame(common_list), DataFrame(required_list)]))
            # turn data
            metaframe = metaframe.transpose()
            # change column labels
            metaframe.columns = metaframe.iloc[0]
            # drop row used as column labels
            metaframe.drop(0, axis=0, inplace=True)
            # reset index
            metaframe.reset_index(drop=True, inplace=True)

            try:
                # write metadata file
                metaframe.to_csv(self._target_meta_filepath, index=False)
                # files copied to archive destination
                copy2(self._data_file, self._target_data_filepath)
            except Exception as err:
                raise CopyError(err)

        # check for successful data copy
        if not path.isfile(self._target_data_filepath):
            message = CopyValidationError.generate_message(self._target_data_filepath)
            raise CopyValidationError(message)

        # check for successful metadata copy
        if not path.isfile(self._target_meta_filepath):
            message = CopyValidationError.generate_message(self._target_meta_filepath)
            raise CopyValidationError(message)
