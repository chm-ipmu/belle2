"""Test for misc/predicted_yields.py"""
import pytest

from constants.mode_info import mode2latex
from misc import predicted_yields


@pytest.mark.parametrize("decay", list(mode2latex.keys()))
def test_predicted_info(decay):
    info = predicted_yields.predicted_info(decay)
    assert type(info) is dict

    for key, val in info.items():
        if key == 'latex':
            assert type(val) is str
            assert val[0] == "$"
            assert val[-1] == "$"
        else:
            assert type(val) is float


def test_table():
    df = predicted_yields.table()
    assert len(df.drop_duplicates()) == len(df)
    assert not df.isnull().any().any()
