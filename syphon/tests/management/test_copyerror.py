"""syphon.tests.management.test_copyerror.py

   Copyright (c) 2017-2018 Keithley Instruments, LLC.
   Licensed under MIT (https://github.com/ehall/syphon/blob/master/LICENSE)

"""
from syphon.management import CopyError

class TestCopyError(object):
    def test_is_exception(self):
        copy_error = CopyError('')
        assert isinstance(copy_error, Exception)

    def test_single_quote_message_storage(self):
        msg = '"This" is a \'test.\''
        copy_error = CopyError(msg)
        assert copy_error.message == msg

    def test_double_quote_message_storage(self):
        msg = "\"This\" is a 'test.'"
        copy_error = CopyError(msg)
        assert copy_error.message == msg

    def test_triple_single_quote_message_storage(self):
        msg = '''"This"
is
a
\'test.\''''
        copy_error = CopyError(msg)
        assert copy_error.message == msg

    def test_triple_double_quote_message_storage(self):
        msg = """\"This\"
is
a
'test.'"""
        copy_error = CopyError(msg)
        assert copy_error.message == msg
