"""syphon.tests.test_context.py

   Copyright Keithley Instruments, LLC.
   Licensed under MIT (https://github.com/ehall/syphon/blob/master/LICENSE)

"""
from syphon import Context


def test_context_archive_property_default():
    assert Context().archive is None


def test_context_cache_property_default():
    assert Context().cache is None


def test_context_data_property_default():
    assert Context().data is None


def test_context_meta_property_default():
    assert Context().meta is None


def test_context_overwrite_property_default():
    assert Context().overwrite is False
    assert isinstance(Context().overwrite, bool)


def test_context_schema_property_default():
    assert Context().schema is None


def test_context_schema_file_property_default():
    assert Context().schema_file is Context()._schema_file
    assert isinstance(Context().schema_file, str)


def test_context_verbose_property_default():
    assert Context().verbose is False
    assert isinstance(Context().verbose, bool)
