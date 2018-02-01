"""syphon.tests.common.test_writeerror.py

   Copyright (c) 2017-2018 Keithley Instruments, LLC.
   Licensed under MIT (https://github.com/ehall/syphon/blob/master/LICENSE)

"""
from syphon.common import WriteError

class TestWriteError(object):
    def test_is_exception(self):
        write_error = WriteError('')
        assert isinstance(write_error, Exception)

    def test_single_quote_message_storage(self):
        msg = '"This" is a \'test.\''
        write_error = WriteError(msg)
        assert write_error.message == msg

    def test_double_quote_message_storage(self):
        msg = "\"This\" is a 'test.'"
        write_error = WriteError(msg)
        assert write_error.message == msg

    def test_triple_single_quote_message_storage(self):
        msg = '''"This"
is
a
\'test.\''''
        write_error = WriteError(msg)
        assert write_error.message == msg

    def test_triple_double_quote_message_storage(self):
        msg = """\"This\"
is
a
'test.'"""
        write_error = WriteError(msg)
        assert write_error.message == msg
