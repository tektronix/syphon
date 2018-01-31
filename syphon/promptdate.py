"""syphon.promptdate.py

   Copyright (c) 2017-2018 Keithley Instruments, LLC.
   Licensed under MIT (https://github.com/ehall/syphon/blob/master/LICENSE)

"""
def prompt_date() -> str:
    """Prompt the user for the date if no metadata file was specified.

    Returns:
        str: Verified date.
    """
    from syphon.verification import verify_date

    while True:
        prompt = '\n  Enter the current date in MM/DD/YYYY format: '
        date = input(prompt)
        verified, message = verify_date(date)
        if not verified:
            print('  > {}\n'.format(message))
        else:
            return date
