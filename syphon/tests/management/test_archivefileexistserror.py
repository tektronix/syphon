"""syphon.tests.management.test_archivefileexistserror.py

   Copyright (c) 2017-2018 Keithley Instruments, LLC.
   Licensed under MIT (https://github.com/ehall/syphon/blob/master/LICENSE)

"""
from syphon.management import ArchiveFileExistsError

class TestArchiveFileExistsError(object):
    def test_is_exception(self):
        afe_error = ArchiveFileExistsError('')
        assert isinstance(afe_error, Exception)

    def test_single_quote_message_storage(self):
        msg = '"This" is a \'test.\''
        afe_error = ArchiveFileExistsError(msg)
        assert afe_error.message == msg

    def test_double_quote_message_storage(self):
        msg = "\"This\" is a 'test.'"
        afe_error = ArchiveFileExistsError(msg)
        assert afe_error.message == msg

    def test_triple_single_quote_message_storage(self):
        msg = '''"This"
is
a
\'test.\''''
        afe_error = ArchiveFileExistsError(msg)
        assert afe_error.message == msg

    def test_triple_double_quote_message_storage(self):
        msg = """\"This\"
is
a
'test.'"""
        afe_error = ArchiveFileExistsError(msg)
        assert afe_error.message == msg
