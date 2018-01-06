"""main.promptreleaseversion.py

   Copyright (c) 2017-2018 Keithley Instruments, LLC.
   Licensed under MIT (https://github.com/ehall/syphon/blob/master/LICENSE)

"""
def prompt_release_version() -> str:
    """Prompt the user for the release version if no metadata file was specified.

    Returns:
        str: Verified release version.
    """
    from verification.verifyreleaseversion import verify_release_version

    # release version
    while True:
        prompt = '\n  Enter the release version in MAJOR.MINOR.PATCH format: '
        release_version = input(prompt)
        verified, message = verify_release_version(release_version)
        if not verified:
            print('  > {}\n'.format(message))
        else:
            return release_version
