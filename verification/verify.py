"""verification.verify.py
   Copyright (c) 2017-2018 Keithley Instruments, LLC.
   Licensed under MIT (https://github.com/ehall/syphon/blob/master/LICENSE)
"""
from common import Metadata
from common import Settings

def verify(metadata: Metadata, settings: Settings) -> (bool, str):
    """Contains methods for performing required filename and metadata verification.

    Args:
        metadata (Metadata): Current metadata container.
        settings (Settings): Current settings container.

    Returns:
        (`bool`, `str`): `False` when metadata is invalid, otherwise `True`. Contains an error
            message when `bool` is `False`, otherwise an empty string.
    """
    from .verifyarch import verify_arch
    from .verifybuildversion import verify_build_version
    from .verifydate import verify_date
    from .verifyreleaseversion import verify_release_version

    message = ''

    # complain if a required tag cannot be found
    required = settings.required_tags       # list
    available_required = metadata.required  # dict

    # for each required metadata tag
    for required_tag in required:
        # if tag cannot be found in available tags
        if required_tag not in list(available_required.keys()):
            message = 'Unable to find required tag  {}.'.format(required_tag)
            return (False, message)
        else:
            # get value of available metadata tag
            value = available_required.get(required_tag)
            # if tag value is not None
            if value is None:
                message = 'Unable to find a value associated with tag  {}.'.format(required_tag)
                return (False, message)
            else:
                if required_tag == 'arch':
                    return verify_arch(value)

                elif required_tag == 'build_version':
                    return verify_build_version(value)

                elif required_tag == 'date':
                    return verify_date(value)

                elif required_tag == 'release_version':
                    return verify_release_version(value)

                else:
                    message = 'Unable to find verification function for tag  {}.'
                    message = message.format(required_tag)
                    return (False, message)
