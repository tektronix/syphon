"""common.settings.py

   Copyright (c) 2017-2018 Keithley Instruments, LLC.
   Licensed under MIT (https://github.com/ehall/syphon/blob/master/LICENSE)

"""
from json import loads
from json import dumps
from os.path import abspath
from os.path import dirname
from os.path import join
from os.path import normpath

class Settings:
    """Contains methods for reading from and writing to the JSON settings file.

    Args:
        settings_file (str): Filepath of the JSON settings file.

    Raises:
        OSError: Failed to read from settings file.
    """
    def __init__(self, settings_file: str):
        # replace backslash with forward slash for consistency
        if '\\' in settings_file:
            self._filepath = settings_file.replace('\\', '/')
        else:
            self._filepath = settings_file

        self._settings_dir = dirname(abspath(settings_file))

        with open(settings_file, 'r', encoding='utf-8') as somefile:
            self._contents = loads(somefile.read())

    @property
    def archive_dir(self) -> str:
        """str: Archive directory path."""
        return normpath(join(self._settings_dir, self._contents['archive']['dir']))

    @archive_dir.setter
    def archive_dir(self, value):
        self._contents['archive']['dir'] = normpath(value)

    @property
    def archive_schema(self) -> dict:
        """:obj:`dict`: Directory storage schema.

        The schema keys are string representations of integer numbers that start at zero and
        increases by one for each unique entry.

        Schema values are metadata tags that must be present for an import to be successful. It's
        that metadata value that is used as the directory location when archiving data.
        For example, if we have the following dictionary object:

            `{ '0': 'release_version', '1': 'build_version'}`

        might result in the target archive path `./archive/0.0.0/123456/`.
        """
        return self._contents['archive']['schema']

    @property
    def data_cache(self) -> str:
        """str: Filepath of data cache."""
        return normpath(join(self._settings_dir, self._contents['data_cache']))

    @property
    def filepath(self) -> str:
        """str: Filepath of the settings file."""
        return normpath(join(self._settings_dir, self._filepath))

    @property
    def get(self) -> dict:
        """:obj:`dict`: Raw data structure of the settings file."""
        return self._contents

    @property
    def metadata_extension(self) -> str:
        """str: Metadata file extension."""
        return self._contents['meta_ext']

    @property
    def required_tags(self) -> list:
        """:obj:`list` of :obj:`str`: Metadata tags required for successful import."""
        tags = list(self._contents['archive']['schema'].values())
        tags += self._contents['verification']['additional_required_tags']
        return tags

    @property
    def version(self) -> str:
        """str: The current program version."""
        return self._contents['version']

    def save(self):
        """Write the new settings to file."""
        with open(self._filepath, 'w', encoding='utf-8') as somefile:
            somefile.write(dumps(self._contents, sort_keys=True, indent=2))
