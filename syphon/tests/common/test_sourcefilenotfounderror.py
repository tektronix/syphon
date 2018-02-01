"""syphon.tests.common.test_sourcefilenotfounderror.py

   Copyright (c) 2017-2018 Keithley Instruments, LLC.
   Licensed under MIT (https://github.com/ehall/syphon/blob/master/LICENSE)

"""
from syphon.common import SourceFileNotFoundError

class TestSourceFileNotFoundError(object):
    def test_is_exception(self):
        sfn_error = SourceFileNotFoundError('')
        assert isinstance(sfn_error, Exception)

    def test_single_quote_message_storage(self):
        msg = '"This" is a \'test.\''
        sfn_error = SourceFileNotFoundError(msg)
        assert sfn_error.message == msg

    def test_double_quote_message_storage(self):
        msg = "\"This\" is a 'test.'"
        sfn_error = SourceFileNotFoundError(msg)
        assert sfn_error.message == msg

    def test_triple_single_quote_message_storage(self):
        msg = '''"This"
is
a
\'test.\''''
        sfn_error = SourceFileNotFoundError(msg)
        assert sfn_error.message == msg

    def test_triple_double_quote_message_storage(self):
        msg = """\"This\"
is
a
'test.'"""
        sfn_error = SourceFileNotFoundError(msg)
        assert sfn_error.message == msg
