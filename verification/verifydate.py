"""verification.verifydate.py

   Copyright (c) 2017-2018 Keithley Instruments, LLC.
   Licensed under MIT (https://github.com/ehall/syphon/blob/master/LICENSE)

"""
def __verify_day(month: str, day: str, year: str):
    """Verify that a day exists given the month and year.

    Args:
        month (str): A two digit month in decimal format.
        day (str): A two digit day in decimal format.
        year (str): A four digit year in decimal format.

    Returns:
        (`bool`, `str`): `False` when `day` does not exist in the given `month` that `year` OR is
            not a decimal, otherwise `True`. Contains an error message when `bool` is `False`,
            otherwise an empty string.
    """
    message = ''

    # verify day (using month and year because nitpicking is fun)
    if day.isdecimal():
        from calendar import monthrange

        _, day_range = monthrange(int(year), int(month))
        day_range = range(1, day_range + 1)

        if (int(day) < day_range[0]) or (int(day) > day_range[-1]):
            from calendar import month_abbr

            message = '{}. {} does not have  {}  days.'
            message = message.format(month_abbr[int(month)], year, day)
            return (False, message)
        else:
            return (True, message)
    else:
        message = 'Day  {}  is not a valid decimal.'.format(day)
        return (False, message)

def __verify_month(month: str):
    """Verify that a given month exists.

    Args:
        month (str): A two digit month in decimal format.

    Returns:
        (`bool`, `str`): `False` when `month` does not exist OR is not a decimal, otherwise `True`.
            Contains an error message when `bool` is `False`, otherwise an empty string.
    """
    message = ''

    # verify month
    if  month.isdecimal():
        if (int(month) < 1) or (int(month) > 12):
            message = 'Years do not have  {}  months.'.format(month)
            return (False, message)
        else:
            return (True, message)
    else:
        message = 'Month  {}  is not a valid decimal.'.format(month)
        return (False, message)


def __verify_year(year: str) -> (bool, str):
    """Verify that a given year is four digits long and is a decimal.

    Apologies in advance if this becomes a problem in the year 10,000.

    Args:
        year (str): A four digit year in decimal format.

    Returns:
        (`bool`, `str`): `False` when `year` is not four digits long OR is not a decimal, otherwise
            `True`. Contains an error message when `bool` is `False`, otherwise an empty string.
    """
    message = ''

    # verify year
    if year.isdecimal():
        if len(year) is not 4:
            message = 'Year  {}  does not follow the YYYY format.'
            return (False, message)
        else:
            return (True, message)
    else:
        message = 'Year  {}  is not a valid decimal.'.format(year)
        return (False, message)

def verify_date(date: str) -> (bool, str):
    """Verify that the date tag is in the MM/DD/YYYY format.

    Note:
        It is important that this function name contains the metadata tag which it tests.

    Args:
        date (str): Date in MM/DD/YYYY format.

    Returns:
        (`bool`, `str`): `False` when `date` is invalid, otherwise `True`. Contains an error
            message when `bool` is `False`, otherwise an empty string.
    """
    result = False
    message = ''

    try:
        month, day, year = date.split('/', 2)
    except ValueError: # when there are less than 3 substrings
        message = 'Date  {}  is not in the MM/DD/YYYY format.'.format(date)
        return (False, message)

    # verify month
    result, message = __verify_month(month)
    if not result:
        return (result, message)

    # verify year
    result, message = __verify_year(year)
    if not result:
        return (result, message)

    # use verified month & year to verify day
    result, message = __verify_day(month, day, year)
    if not result:
        return (result, message)

    return (True, message)
