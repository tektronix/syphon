"""main.promptswitch.py

   Copyright (c) 2017-2018 Keithley Instruments, LLC.
   Licensed under MIT (https://github.com/ehall/syphon/blob/master/LICENSE)

"""
from common.settings import Settings

def prompt_switch(root: str, settings: Settings) -> str:
    """Prompt the user for the new archive directory if none was specified.

    Args:
        root (str): Highest level of the program directory.
        settings (Settings): Current settings container.

    Returns:
        str: New archive directory if one was specified, otherwise an empty string.
    """
    from os import mkdir
    from os import path

    while True:
        notice = '\n  The current archive directory is: {}'.format(settings.archive_dir)
        print(notice)
        prompt = '  Would you like to change the archive directory? (y/N) '
        answer = input(prompt)

        if len(answer) == 0:
            answer = 'n'

        answer = answer.lower()

        if answer[0] == 'y':
            prompt = '  Enter the name of the new archive directory: '
            name = input(prompt)

            new_dir = path.join(root, name)
            if not path.exists(new_dir):
                mkdir(new_dir)

            return name

        elif answer[0] == 'n':
            return ''

        else:
            print('  Invalid response {}.'.format(answer))
