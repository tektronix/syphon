#!python3
"""syphon.py

   Copyright (c) 2017-2018 Keithley Instruments, LLC.
   Licensed under MIT (https://github.com/ehall/syphon/blob/master/LICENSE)

"""
if __name__ == '__main__':
    from os.path import dirname
    from sys import argv

    from main import syphon

    exit(syphon(dirname(__file__), argv))
