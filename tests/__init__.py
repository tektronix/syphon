"""tests.__init__.py

   Copyright Keithley Instruments, LLC.
   Licensed under MIT (https://github.com/tektronix/syphon/blob/master/LICENSE)

"""
from random import choice
from string import ascii_letters, digits
from typing import Any, Callable, List, Optional

from pandas import DataFrame


def get_data_path() -> str:
    """Return an absolute path to the dataset directory.

    Returns:
        str: Absolute path to the data directory.
    """
    from os.path import abspath, dirname, join

    return join(abspath(dirname(__file__)), "data")


def make_dataframe(
    nrows: int, ncols: int, data_gen_f: Optional[Callable[[int, int], Any]] = None
) -> DataFrame:
    """Local mapping of `pandas.util.testing.makeCustomDataframe`.

    Resulting `DataFrame` will have neither a columns name nor an index
    name. Indices will be a zero-based integer list.

    Parameter names and descriptions are based on those found in
    `pandas.util.testing.py`.
        https://github.com/pandas-dev/pandas/blob/f483321/pandas/util/testing.py

    Args:
        nrows (int): Number of rows.
        ncols (int): Number of columns.
        data_gen_f (func): Function f(row,col) that returns a value for
            the given position.

    Returns:
        DataFrame: Generated `DataFrame` object.
    """
    from pandas.util.testing import makeCustomDataframe

    # pandas bug (?) in makeCustomIndex when nentries = 1
    if ncols == 1:
        return DataFrame(
            {"C_l0_g0": [make_dataframe_value(x, 0) for x in range(nrows)]}
        )
    else:
        return makeCustomDataframe(
            nrows,
            ncols,
            c_idx_names=False,
            r_idx_names=False,
            data_gen_f=data_gen_f,
            r_idx_type="i",
        )


def make_dataframe_value(nrows: int, ncols: int) -> str:
    """The default value generator for
    `pandas.util.testing.makeCustomDataframe`.

    Parameter names and descriptions are based on those found in
    `pandas.util.testing.py`.
        https://github.com/pandas-dev/pandas/blob/f483321/pandas/util/testing.py

    Args:
        nrows (int): Number of rows.
        ncols (int): Number of columns.

    Returns:
        str: "RxCy" based on the given position.
    """
    return f"R{nrows}C{ncols}"


def rand_string(size: int = 6) -> str:
    """Generate a random string from the set of a-z, A-Z, and 0-9.

    Args:
        size: Length of the random string. Default is 6.

    Returns:
        str: Random string.
    """
    return "".join(choice(ascii_letters + digits) for _ in range(size))


def randomize(*args: Any) -> List[Any]:
    """Randomize the order of the given arguments."""
    arguments = list(args)
    result = []
    while len(arguments) > 0:
        index: int = choice([i for i in range(0, len(arguments))])
        result.append(arguments.pop(index))
    return result
