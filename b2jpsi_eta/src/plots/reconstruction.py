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
from typing import List, Optional, Iterable

import matplotlib.pyplot as plt
import pandas as pd
import root_pandas as rpd
import seaborn as sns

from constants.locations import PLOTS_DIR, PROJECT_ROOT


def get_sig_and_bkg_series(decay, var, range=None):
    # Processing data
    where = f"{var} > {range[0]} && {var} < {range[1]}" if range is not None else None
    tree = _read_decay(decay=decay, where=where)
    is_signal = tree.isSignal.astype(bool)
    signal = tree[is_signal]
    background = tree[~is_signal]
    return background, signal


def _read_decay(decay: str, where: Optional[str] = None, columns: List[str] = None, key: str = "b0") -> pd.DataFrame:
    """
    Take a merged, reconstructed decay .root file and return it is a pandas DataFrame
    :param decay: Specify the decay you want the .root file of. One of the names defined in the
    dec_files folder
    :param where: An optional cut to supply to reduce DataFrame before returning it
    :param columns: List of names of columns to include in DataFrame. May be needed to keep memory
    usage low
    :param key: Name of the tree within the .root file
    :return: .root file represented as a pandas DataFrame
    """
    default_columns = "Mbc deltaE isSignal".split()
    columns = columns if columns is not None else default_columns
    tree = rpd.read_root(os.path.join(PROJECT_ROOT, "merged", f"root_files/{decay}.root"), columns=columns, where=where,
                         key=key)
    return tree


def plot_sig_vs_bkg(decay: str, var: str, range: Iterable[float], bins: int = 100,
                    latex: Optional[str] = None) -> None:
    """
    Make a plot showing signal and background distributions for variable var, default "Mbc"
    :param latex: Optional LaTeX string for x-axis label
    :param decay: Specify decay to plot data from
    :param var: Specify variable to plot
    :param range: Specify range to plot over
    :param bins: Specify number of bins when making histograms
    :return: None
    """
    # Initial formatting for plots
    plt.rc("text", usetex=True)
    sns.set(context="paper", font_scale=1.1, style="ticks", palette="pastel")

    background, signal = get_sig_and_bkg_series(decay, var, range)
    fig, (sig_ax, bkg_ax) = plt.subplots(nrows=2, sharex=True)

    # Plot signal
    sig_color = "green"
    signal.hist(var, bins=bins, histtype="step", color=sig_color, ax=sig_ax, range=range,
                label="Signal")

    # Plot background
    bkg_color = "red"
    background.hist(var, bins=bins, histtype="step", color=bkg_color, ax=bkg_ax, range=range,
                    label="Background")

    # Draw statistics box
    for ax, data in zip((sig_ax, bkg_ax), (signal, background)):
        xpos = 0.82
        if ax == sig_ax and var == "Mbc":
            xpos = 0.22

        total = len(data)
        std_dev = data[var].std()
        text = (
            r"\begin{tabular}{cc}"
            f"Total & {round(total)} \\\\"
            f"$\\sigma$ & {std_dev:.4f} \\\\"
            r"\end{tabular}"
        )

        ax.annotate(text, xy=(xpos, 0.55), xycoords="axes fraction")

    # Final formatting
    bkg_ax.set(title=None, ylabel="Candidates")
    bkg_ax.legend(loc="best")
    sig_ax.set(title=None, ylabel="Candidates")
    sig_ax.legend(loc="best")
    bkg_ax.set_xlabel(var if latex is None else latex)
    plt.tight_layout()

    # Save plot
    plot_path = os.path.join(PLOTS_DIR, "reconstruction", f"{decay}_{var}_sig_vs_bkg.pdf")
    plt.savefig(plot_path)


def plot_sig_vs_bkg_Mbc(decay: str) -> None:
    plot_sig_vs_bkg(decay=decay, var="Mbc", range=(4.9, 5.3), latex="$M_{bc}$ / GeV")


def plot_sig_vs_bkg_deltaE(decay: str) -> None:
    plot_sig_vs_bkg(decay=decay, var="deltaE", range=(-0.5, 0.5), latex="$\Delta E$ / GeV")


def plot_joint(decay: str, sig_or_bkg: str) -> None:
    e_lower = -0.2
    e_upper = 0.2
    m_lower = 5.27
    m_upper = 5.285
    is_sig = sig_or_bkg == "sig"
    if is_sig:
        where = f"isSignal && deltaE < {e_upper} && deltaE > {e_lower} && Mbc > {m_lower} && Mbc < {m_upper}"
        c = "g"
    else:
        where = f"isSignal!=1 && deltaE < {e_lower} && deltaE > -5 && Mbc > 4.5"
        c = "magenta"

    tree = _read_decay(decay=decay, where=where)
    grid = (
        sns.jointplot(x="Mbc", y="deltaE", data=tree, color=c, kind="hex")
            .set_axis_labels(
            "$M_{bc}$ / GeV",
            "$\Delta E$ / GeV"
        )
    )

    # Draw a signal region box if you are looking at background plots
    if not is_sig:
        grid.ax_joint.axhline(e_lower, c="red", lw=2, ls='--')
        grid.ax_joint.axhline(e_upper, c="red", lw=2, ls='--')

        grid.ax_joint.axvline(m_lower, c="red", lw=2, ls='--')
        grid.ax_joint.axvline(m_upper, c="red", lw=2, ls='--')

    grid.savefig(
        os.path.join(PLOTS_DIR, "reconstruction", f"{decay}_{sig_or_bkg}_joint.pdf")
    )


if __name__ == '__main__':
    import sys

    func, *args = sys.argv[1:]
    funcs = {
        'plot_sig_vs_bkg': plot_sig_vs_bkg,
        'plot_sig_vs_bkg_Mbc': plot_sig_vs_bkg_Mbc,
        'plot_sig_vs_bkg_deltaE': plot_sig_vs_bkg_deltaE,
        'plot_joint': plot_joint,
    }
    func = funcs[func]
    print(f"Calling {func} with args: {args}")
    func(*args)
