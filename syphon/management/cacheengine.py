"""syphon.management.cacheengine.py

   Copyright (c) 2017-2018 Keithley Instruments, LLC.
   Licensed under MIT (https://github.com/ehall/syphon/blob/master/LICENSE)

"""
from os import path

from pandas import concat
from pandas import DataFrame
from pandas import read_csv
from pandas import Series

from syphon.common import ReadError
from syphon.common import SourceFileNotFoundError
from syphon.common import WriteError

from .columnexistserror import ColumnExistsError

class CacheEngine:
    """Contains methods for performing data caching.

    Args:
        master_data_file (str): Filepath of the data cache.
        collated_data_file (str): Filepath of an archived data file.
        collated_metadata_file (str): Filepath of an archived metadata file.
    """
    def __init__(self,
                 master_data_file: str,
                 collated_data_file: str,
                 collated_metadata_file: str
                ):
        self._master_data_file = master_data_file
        self._collated_data_file = collated_data_file
        self._collated_metadata_file = collated_metadata_file

    def cache_import_data(self, flat_import_data: DataFrame):
        """Merge a `DataFrame` into the data cache.

        Args:
            flat_import_data (DataFrame): A `DataFrame` object containing a set of data
                and associated metadata.

        Raises:
            ReadError: An error occurred during the read operation.
            WriteError: An error occurred during a write operation.
        """
        try:
            # check for existance of master
            if not path.exists(self._master_data_file):
                #   if it doesn't exist, then export current data as master
                flat_import_data.to_csv(self._master_data_file, index=False)
                return
        except Exception as err:
            raise WriteError(err)

        # else read cache
        cache = DataFrame()
        try:
            cache = DataFrame(read_csv(self._master_data_file, dtype=str))
        except Exception as err:
            raise ReadError(err)

        # merge
        result = cache.append(flat_import_data)

        # reset numbering
        result.reset_index(drop=True, inplace=True)

        try:
            # save master
            result.to_csv(self._master_data_file, index=False)
        except Exception as err:
            raise WriteError(err)

    def flatten_file_pair(self) -> DataFrame:
        """Return data and metadata files as a single `DataFrame`.

        The data and metadata paths used are those passed to the `CacheEngine` constructor.

        Raises:
            ReadError: An error occurred during a read operation.
            SourceFileNotFoundError: Data or metadata file cannot be found.
        """
        from pandas.io.common import CParserError
        from .purge import purge_file

        # ensure everything is still valid
        if not path.exists(self._collated_data_file):
            raise SourceFileNotFoundError(
                'Caching error. '
                'Unable to locate source file {}'
                .format(self._collated_data_file)
            )

        if not path.exists(self._collated_metadata_file):
            raise SourceFileNotFoundError(
                'Caching error. '
                'Unable to locate source file {}'
                .format(self._collated_metadata_file)
            )

        # read data
        data = DataFrame()
        try:
            with open(self._collated_data_file, 'r') as data_target:
                data = DataFrame(read_csv(data_target, dtype=str, comment='#'))
        except CParserError:
            message = 'Unable to parse data file  {}'
            message = message.format(path.basename(self._collated_data_file))
            purge_file(self._collated_data_file)
            purge_file(self._collated_metadata_file)
            raise ReadError(message)
        except Exception as err:
            raise ReadError(err)

        # remove any 'Unnamed' columns
        data.dropna(axis=1, how='all', inplace=True)

        # if there's just one value at the top of the column,
        # then repeat it for the whole column
        for column in data:
            # if this column has one non-nan value
            if data[column].count() == 1:
                # get the only value from this column
                value = data[column].dropna(axis=0, how='any').values[0]
                # replace all nan values in this column with this value
                data[column].fillna(value, axis=0, inplace=True)

        # read metadata
        metadata = DataFrame()
        try:
            with open(self._collated_metadata_file, 'r') as meta_target:
                metadata = DataFrame(read_csv(meta_target, dtype=str))
        except CParserError:
            message = 'Unable to parse meta file  {}'
            message = message.format(path.basename(self._collated_metadata_file))
            purge_file(self._collated_data_file)
            purge_file(self._collated_metadata_file)
            raise ReadError(message)
        except Exception as err:
            raise ReadError(err)

        # remove any 'Unnamed' columns
        metadata.dropna(axis=1, how='all', inplace=True)

        # get max rows
        total_datapoints, _ = data.shape

        # add metadata to data
        for column_header in metadata.columns:
            # check if column already exists
            if column_header in data.columns:
                message = ("Unable to merge\n"
                           "\t{}\n"
                           "into\n"
                           "\t{}.\n"
                           "Column  {}  already exists."
                          )
                message = message.format(self._collated_metadata_file,
                                         self._collated_data_file,
                                         column_header
                                        )
                raise ColumnExistsError(message)

            # create list that contains metadata value repeated  total_datapoints  times
            # metadata values not existing is caught by Verifier
            series = Series([metadata[column_header].iloc[0]] * total_datapoints,
                            name=column_header
                           )
            data = concat([data, series], axis=1)

        return data

    @staticmethod
    def rebuild_data_cache(archive_dir: str,
                           metadata_file_ext: str,
                           master_data_file: str,
                           verbose: bool
                          ):
        """Recache all data, metadata file pairs found in the given archive directory.

        Args:
            archive_dir (str): Directory location of historic data storage.
            metadata_file_ext (str): The metadata file extension.
            master_data_file (str): Filepath of the data cache.
            verbose (bool): Report progress if `True`, otherwise remain silent.
        """
        from glob import glob
        from os import walk
        from os.path import join

        metadata_list = []
        file_list = []

        if verbose:
            print(' Searching archives ... ', end='')

        # start a directory tree walk
        for (dirpath, _, filenames) in walk(archive_dir):
            # if files were found
            if filenames:
                # list of absolute filepaths
                abs_filenames = []
                # make absolute path for each found file
                for somefile in filenames:
                    abs_filenames += [join(dirpath, somefile)]
                # add filenames to file_list
                file_list += abs_filenames
                # get metadata files from filenames
                metadata_list += glob(path.join(dirpath, '*{}'.format(metadata_file_ext)))

        if verbose:
            print('Done')

            # get the total number of non-metadata files
            # (subtract number of metadata files from the number of all files)
            f_list_len = len(file_list) - len(metadata_list)
            # get the total number of metadata files
            # (subtract number of non-metadata files from the number of all files)
            m_list_len = len(file_list) - f_list_len
            print(' Found {} metadata files and {} others.'.format(m_list_len, f_list_len))

            print(' Caching file pairs ...     ', end='', flush=True)

        # current loop count
        current_count = 0
        # cached file pairs stat tracker
        cache_count = 0
        # for each file found during the archive search
        for data_file in file_list:
            # skip if file is a metadata file
            if not metadata_file_ext in path.splitext(data_file)[-1]:
                # get name of data file
                data_name, _ = path.splitext(path.basename(data_file))
                # find matching metadata file
                for metadata_file in metadata_list:
                    # get name of metadata file
                    meta_name, _ = path.splitext(path.basename(metadata_file))

                    # if we found a file pair
                    if data_name == meta_name:
                        # perform an import (we can skip the verification)
                        cache_engine = CacheEngine(master_data_file, data_file, metadata_file)
                        flat_data = cache_engine.flatten_file_pair()
                        cache_engine.cache_import_data(flat_data)

                        # shorten the list of metadata files to shorten runtime
                        metadata_list.remove(metadata_file)

                        # increment the cached file pair stat by one
                        cache_count += 1

                        # jump to next item in data file list
                        break

            # increment loop count
            current_count += 1

            # update percent complete
            if verbose:
                print('{0}{0}{0}{0}'.format('\x08'), end='', flush=True)
                print('{:>4.0%}'.format(current_count/len(file_list)), end='', flush=True)

        if verbose:
            print()
            print(' Cached {} file pairs.'.format(cache_count))

        return
