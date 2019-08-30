"""syphon.tests.test_main.py

   Copyright Keithley Instruments, LLC.
   Licensed under MIT (https://github.com/tektronix/syphon/blob/master/LICENSE)

"""
from typing import List

from _pytest.capture import CaptureFixture, CaptureResult

from syphon import __version__
from syphon.__main__ import _main


def test_main_version(capsys: CaptureFixture):
    arguments: List[str] = ["syphon", "--version"]
    _main(arguments)
    output: CaptureResult = capsys.readouterr()
    assert output.out == "{}\n".format(__version__)
