"""verification.verifyreleaseversion.py

   Copyright (c) 2017-2018 Keithley Instruments, LLC.
   Licensed under MIT (https://github.com/ehall/syphon/blob/master/LICENSE)

"""
def verify_release_version(release_version: str) -> (bool, str):
    """Verify that the release version tag is in the MAJOR.MINOR.PATCH format.

    Note:
        It is important that this function name contains the metadata tag which it tests.

    Args:
        release_version (str): Release version tag in MAJOR.MINOR.PATCH format.

    Returns:
        (`bool`, `str`): `False` when `release_version` is not in the MAJOR.MINOR.PATCH format,
            otherwise `True`. Contains an error message when `bool` is `False`, otherwise an empty
            string.
    """
    import re

    result = False
    message = ''
    regex = r"^(?P<major>\d+)(?:[.])(?P<minor>\d+)(?:[.])(?P<patch>\d+)"

    matches = re.findall(regex, release_version, re.MULTILINE)

    if not matches:
        message = 'Release version  {}  does not follow the MAJOR.MINOR.PATCH format.'
        message = message.format(release_version)
    else:
        result = True

    return (result, message)
