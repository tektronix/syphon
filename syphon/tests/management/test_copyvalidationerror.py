"""syphon.tests.management.test_copyvalidationerror.py

   Copyright (c) 2017-2018 Keithley Instruments, LLC.
   Licensed under MIT (https://github.com/ehall/syphon/blob/master/LICENSE)

"""
from syphon.management import CopyValidationError

class TestCopyValidationError(object):
    def test_is_exception(self):
        cv_error = CopyValidationError('')
        assert isinstance(cv_error, Exception)

    def test_single_quote_message_storage(self):
        msg = '"This" is a \'test.\''
        cv_error = CopyValidationError(msg)
        assert cv_error.message == msg

    def test_double_quote_message_storage(self):
        msg = "\"This\" is a 'test.'"
        cv_error = CopyValidationError(msg)
        assert cv_error.message == msg

    def test_triple_single_quote_message_storage(self):
        msg = '''"This"
is
a
\'test.\''''
        cv_error = CopyValidationError(msg)
        assert cv_error.message == msg

    def test_triple_double_quote_message_storage(self):
        msg = """\"This\"
is
a
'test.'"""
        cv_error = CopyValidationError(msg)
        assert cv_error.message == msg
