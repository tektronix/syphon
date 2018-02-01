"""syphon.tests.common.test_archivenotfounderror.py

   Copyright (c) 2017-2018 Keithley Instruments, LLC.
   Licensed under MIT (https://github.com/ehall/syphon/blob/master/LICENSE)

"""
from syphon.common import ArchiveNotFoundError

class TestArchiveNotFoundError(object):
    def test_is_exception(self):
        anf_error = ArchiveNotFoundError('')
        assert isinstance(anf_error, Exception)

    def test_single_quote_message_storage(self):
        msg = '"This" is a \'test.\''
        anf_error = ArchiveNotFoundError(msg)
        assert anf_error.message == msg

    def test_double_quote_message_storage(self):
        msg = "\"This\" is a 'test.'"
        anf_error = ArchiveNotFoundError(msg)
        assert anf_error.message == msg

    def test_triple_single_quote_message_storage(self):
        msg = '''"This"
is
a
\'test.\''''
        anf_error = ArchiveNotFoundError(msg)
        assert anf_error.message == msg

    def test_triple_double_quote_message_storage(self):
        msg = """\"This\"
is
a
'test.'"""
        anf_error = ArchiveNotFoundError(msg)
        assert anf_error.message == msg
