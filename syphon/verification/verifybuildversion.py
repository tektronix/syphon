"""syphon.verification.verifybuildversion.py

   Copyright (c) 2017-2018 Keithley Instruments, LLC.
   Licensed under MIT (https://github.com/ehall/syphon/blob/master/LICENSE)

"""
def verify_build_version(build_version: str) -> (bool, str):
    """Verifies that the build version tag is a decimal value.

    Note:
        It is important that this function name contains the metadata tag which it tests.

    Args:
        build_version (str): Build version metadata tag.

    Returns:
        (`bool`, `str`): `False` when `build_version` is not a decimal, otherwise `True`. Contains
            an error message when `bool` is `False`, otherwise an empty string.
    """
    result = str.isdecimal(build_version)
    message = ''

    if not result:
        message = 'Build version  {}  is not a valid decimal.'.format(build_version)

    return (result, message)
