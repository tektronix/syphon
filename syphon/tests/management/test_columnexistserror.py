"""syphon.tests.management.test_columnexistserror.py

   Copyright (c) 2017-2018 Keithley Instruments, LLC.
   Licensed under MIT (https://github.com/ehall/syphon/blob/master/LICENSE)

"""
from syphon.management import ColumnExistsError

class TestColumnExistsError(object):
    def test_is_exception(self):
        ce_error = ColumnExistsError('')
        assert isinstance(ce_error, Exception)

    def test_single_quote_message_storage(self):
        msg = '"This" is a \'test.\''
        ce_error = ColumnExistsError(msg)
        assert ce_error.message == msg

    def test_double_quote_message_storage(self):
        msg = "\"This\" is a 'test.'"
        ce_error = ColumnExistsError(msg)
        assert ce_error.message == msg

    def test_triple_single_quote_message_storage(self):
        msg = '''"This"
is
a
\'test.\''''
        ce_error = ColumnExistsError(msg)
        assert ce_error.message == msg

    def test_triple_double_quote_message_storage(self):
        msg = """\"This\"
is
a
'test.'"""
        ce_error = ColumnExistsError(msg)
        assert ce_error.message == msg
