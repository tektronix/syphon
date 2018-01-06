"""verification.verifyarch.py

   Copyright (c) 2017-2018 Keithley Instruments, LLC.
   Licensed under MIT (https://github.com/ehall/syphon/blob/master/LICENSE)

"""
def verify_arch(arch: str) -> (bool, str):
    """Verifies that the given string is either `i386` or `x86_64`.

    Note:
        It is important that this function name contains the metadata tag which it tests.

    Args:
        arch (str): System architecture metadata tag.

    Returns:
        (`bool`, `str`): `False` when `arch` is neither `i386` nor `x86_64`, otherwise `True`.
            Contains an error message when `bool` is `False`, otherwise an empty string.
    """
    result = arch == 'i386' or arch == 'x86_64'
    message = ''

    if not result:
        message = 'Architecture  {}  is not a supported instruction set.'.format(arch)

    return (result, message)
