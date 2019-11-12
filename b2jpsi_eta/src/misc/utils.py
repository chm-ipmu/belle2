"""misc/utils.py
Generally handy stuff for the analysis
"""

from typing import Optional, List

import pandas as pd


def get_merged_file(decay: str) -> str:
    """
    Just returns the file location of the merged .root file for the supplied mode
    :param decay: The decay mode in question
    :return: A string representing the location of the merged file
    """
    import os
    from constants.locations import MERGED_FILES
    path = os.path.join(MERGED_FILES, f"{decay}.root")
    return path


def get_merged_df(decay: str, key: Optional[str] = "b0", where: Optional[str] = None,
                  columns: Optional[List[str]] = None) -> pd.DataFrame:
    """
    Returns a pandas DataFrame for the merged .root file of the specified decay
    :param decay: The decay you want
    :param key: The tree within the .root file you want
    :param where: Optional cuts to apply before returning
    :param columns: Columns you want in the DataFrame
    :return: pandas DataFrame
    """
    import root_pandas
    path = get_merged_file(decay=decay)
    df = root_pandas.read_root(path, key=key, columns=columns, where=where)
    return df
