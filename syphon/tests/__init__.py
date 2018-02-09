"""syphon.tests.__init__.py

   Copyright (c) 2017-2018 Keithley Instruments, LLC.
   Licensed under MIT (https://github.com/ehall/syphon/blob/master/LICENSE)

"""
from pandas import DataFrame

def get_data_path() -> str:
    """Return an absolute path to the dataset directory.

    Returns:
        str: Absolute path to the data directory.
    """
    from os.path import abspath, dirname, join

    return join(abspath(dirname(__file__)), 'data')

def make_dataframe(nrows: int, ncols: int, data_gen_f=None) -> DataFrame:
    """Local mapping of `pandas.util.testing.makeCustomDataframe`.

    Resulting `DataFrame` will have neither a columns name nor an index name.
    Indices will be a zero-based integer list.

    Parameter names and descriptions are based on those found in
    `pandas.util.testing.py`.
        https://github.com/pandas-dev/pandas/blob/f483321/pandas/util/testing.py

    Args:
        nrows (int): Number of rows.
        ncols (int): Number of columns.
        data_gen_f (func): Function f(row,col) that returns a value for the
            given position.

    Returns:
        DataFrame: Generated `DataFrame` object.
    """
    from pandas.util.testing import makeCustomDataframe

    return makeCustomDataframe(nrows, ncols,
                               c_idx_names=False, r_idx_names=False,
                               data_gen_f=data_gen_f, r_idx_type='i')

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
    return 'R{}C{}'.format(nrows, ncols)
