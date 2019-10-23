# A script to compare the different branching ratios which go into b02jpsi_eta decays
import os

import constants.branching_ratios as br
import matplotlib.pyplot as plt
from constants.locations import KEKCC_HOME

plt.rc('text', usetex=True)
colors = ["tab:blue", "tab:green", "tab:red", "tab:purple"]


def fmt(x):
    return format(x, ".1f") + "\%"


def make_pie(particle, decay_products, decay_fractions, path):
    fig, ax = plt.subplots()
    plt.title(f"Branching fraction of ${particle}$")

    # Add final slice for remainder
    remainder = 1 - sum(decay_fractions)
    explode = [0] * (len(decay_fractions)) + [0.1]
    colors_ = colors[:len(decay_products)] + ['gray']
    sizes = decay_fractions + [remainder]
    labels = decay_products + ["Remainder"]

    plt.pie(sizes, labels=labels, autopct=fmt, shadow=True,
            colors=colors_, explode=explode)

    plt.savefig(path)


if __name__ == '__main__':
    # r"$B \rightarrow J/\psi \eta$",

    jpsi_modes = [
        r"$ee$",
        r"$\mu\mu$",
    ]
    jpsi_fractions = [
        br.jpsi2ee,
        br.jpsi2mumu,
    ]
    jpsi_fractions = [x[0] for x in jpsi_fractions]

    eta_modes = [
        r"$\gamma\gamma$",
        r"$\pi^0\pi^0\pi^0$",
        r"$\pi\pi\pi^0$",
        r"$\pi\pi\gamma$",
    ]
    eta_fractions = [
        br.eta2gammagamma,
        br.eta23pi0,
        br.eta2pipipi0,
        br.eta2pipigamma
    ]
    eta_fractions = [x[0] for x in eta_fractions]

    home = os.path.join(KEKCC_HOME, 'b2jpsi_eta', 'plots', 'misc', 'brs')

    make_pie(r"\eta", decay_products=eta_modes, decay_fractions=eta_fractions, path=os.path.join(home, "eta.pdf"))
    make_pie(r"J/\psi", decay_products=jpsi_modes, decay_fractions=jpsi_fractions, path=os.path.join(home, "jpsi.pdf"))
