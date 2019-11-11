"""plots/reconstruction.py
Make some plots from reconstructed events.
Usage:
    $ python plots/reconstruction.py <func> [<args>,...]
Functions:
    - plot_sig_vs_bkg
"""

# TODO:
#  - doctests/strings
#  - integration into snakefile
#  - Label plots, add features, etc...

import os
from typing import List, Optional

import matplotlib.pyplot as plt
import pandas as pd
import root_pandas as rpd

from constants.locations import PLOTS_DIR, PROJECT_ROOT


def _read_decay(decay: str, where: Optional[str] = None, columns: List[str] = None, key: str = "b0") -> pd.DataFrame:
    """

    :param decay:
    :param where:
    :param columns:
    :param key:
    :return:
    """
    columns = columns if columns is not None else "Mbc deltaE isSignal".split()
    tree = rpd.read_root(os.path.join(PROJECT_ROOT, "merged", f"root_files/{decay}.root"), columns=columns, where=where,
                         key=key)
    return tree


def plot_sig_vs_bkg(decay: str, bins: int = 100) -> None:
    """

    :param decay:
    :param bins:
    :return:
    """
    tree = _read_decay(decay=decay)
    is_signal = tree.isSignal.astype(bool)
    signal = tree[is_signal]
    background = tree[~is_signal]
    fig, (sig_ax, bkg_ax) = plt.subplots(nrows=2, sharex=True)
    range = (4.9, 5.3)
    # Plot signal
    sig_color = "green"
    signal.hist("Mbc", bins=bins, histtype="step", color=sig_color, ax=sig_ax, range=range)
    # Plot background
    bkg_color = "red"
    background.hist("Mbc", bins=bins, histtype="step", color=bkg_color, ax=bkg_ax, range=range)
    # Save plot
    plt.savefig(os.path.join(PLOTS_DIR, "reconstruction", f"{decay}_sig_vs_bkg.pdf"))


if __name__ == '__main__':
    import sys

    func, *args = sys.argv[1:]
    funcs = {
        'plot_sig_vs_bkg': plot_sig_vs_bkg
    }
    func = funcs[func]
    print(f"Calling {func} with args: {args}")
    func(*args)
