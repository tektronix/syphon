"""syphon.tests.test_getdataextension.py

   Copyright (c) 2017-2018 Keithley Instruments, LLC.
   Licensed under MIT (https://github.com/ehall/syphon/blob/master/LICENSE)

"""
from syphon import get_data_extension

def test_absolute_path(dataset_factory, extension_fixture):
    import re
    from os import walk
    from os.path import abspath, basename, join, splitext

    # make path absolute
    path = abspath(dataset_factory)

    # make regex file pattern matcher
    extension_regex = re.compile('.*{}'.format(extension_fixture))

    metadata_file = None
    # get name of file with the matching extension
    for _, _, files in walk(path):
        for f in files:
            if extension_regex.match(f):
                metadata_file = f
                break

    if metadata_file:
        # get the filename with no extension
        filename, _ = splitext(basename(metadata_file))

        # make new regex
        filename_regex = re.compile('{}.*'.format(filename))

        data_file = None
        # get file with a matching name
        for _, _, files in walk(path):
            for f in files:
                if filename_regex.match(f):
                    if extension_regex.match(f):
                        continue
                    else:
                        data_file = f
                        break

        # expected
        _, expected_extension = splitext(data_file)
    else:
        expected_extension = None

    # test
    actual_extension = get_data_extension(path, extension_fixture)

    assert actual_extension == expected_extension

def test_relative_path(dataset_factory, extension_fixture):
    import re
    from os import walk
    from os.path import basename, dirname, join, relpath, splitext

    # get relative path to the temp directory
    path = relpath(dataset_factory, start=dirname(__file__))

    # make regex file pattern matcher
    extension_regex = re.compile('.*{}'.format(extension_fixture))

    metadata_file = None
    # get name of file with the matching extension
    for _, _, files in walk(path):
        for f in files:
            if extension_regex.match(f):
                metadata_file = f
                break

    if metadata_file:
        # get the filename with no extension
        filename, _ = splitext(basename(metadata_file))

        # make new regex
        filename_regex = re.compile('{}.*'.format(filename))

        data_file = None
        # get file with a matching name
        for _, _, files in walk(path):
            for f in files:
                if filename_regex.match(f):
                    if extension_regex.match(f):
                        continue
                    else:
                        data_file = f
                        break

        # expected
        _, expected_extension = splitext(data_file)
    else:
        expected_extension = None

    # test
    actual_extension = get_data_extension(path, extension_fixture)

    assert actual_extension == expected_extension
