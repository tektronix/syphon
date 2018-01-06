"""main.promptbuildversion.py

   Copyright (c) 2017-2018 Keithley Instruments, LLC.
   Licensed under MIT (https://github.com/ehall/syphon/blob/master/LICENSE)

"""
def prompt_build_version() -> str:
    """Prompt the user for the build version if no metadata file was specified.

    Returns:
        str: Verified build version.
    """
    from verification.verifybuildversion import verify_build_version

    # build version
    while True:
        prompt = '\n  Enter the engineering build version as a whole number: '
        build_version = input(prompt)
        verified, message = verify_build_version(build_version)
        if not verified:
            print('  > {}\n'.format(message))
        else:
            return build_version
