"""efficiencies/detection.py
Simple script to tabulate selection efficiencies
"""

import attr

from constants.mode_info import mode2latex
from misc.utils import get_merged_df


@attr.s
class DetectionEfficiencyRow:
    decay: str = attr.ib()

    def __attrs_post_init__(self):
        self.tree = get_merged_df(self.decay, columns=["isSignal"])
        self.N_GEN = 10000  # TODO: Update this when cuts are optimised and you're running on more than 10*1000 events.

    @staticmethod
    def latex(x, fmt=None):
        return f"${x}$" if fmt is None else f"${x:{fmt}}$"

    @staticmethod
    def truth_match(tree):
        mask = tree["isSignal"]
        return tree[mask]

    @property
    def nsig(self):
        return sum(self.tree["isSignal"])

    @property
    def eff(self):
        return self.nsig / self.N_GEN

    @property
    def predicted_yield(self):
        from misc import predicted_yields
        return predicted_yields.predicted_info(self.decay)["tot"]

    @property
    def row(self):
        mode = self.latex(mode2latex[self.decay])
        nsig_latex = self.latex(self.nsig)
        eff_det = self.latex(self.eff, fmt="0.2%").replace("%", "\\%")
        pred = format(self.predicted_yield, ".2f")
        row = f"{mode} & {self.N_GEN} & {nsig_latex} & {eff_det} & {pred} \\\\" + "\n"
        return row


@attr.s
class DetectionEfficiencyTable:
    path: str = attr.ib()

    def get_rows(self):
        rows = [
            DetectionEfficiencyRow(decay).row
            for decay in mode2latex
        ]
        return rows

    def _table(self):
        table = [
            r"\begin{table}",
            r"\caption{Summary of detection efficiencies for each mode studied in this analysis.}",
            r"\label{tab:det_effs}",
            r"\begin{tabular}{ccccc}",
            r"\hline",
            r"Mode & \# Gen & \# Signal & $\epsilon_{Det}$ & Pred. Yield \\"
            r"\hline\hline"
        ]
        table.extend(self.get_rows())
        table.extend([
            r"\end{tabular}",
            r"\end{table}"
        ])
        return "\n".join(table)

    def table(self):
        with open(self.path, 'w') as f:
            f.write(self._table())


if __name__ == '__main__':
    import pprint
    import os
    from constants.locations import PROJECT_ROOT

    print("Making detection efficiency table for modes:")
    pprint.pprint(list(mode2latex.keys()))

    table = DetectionEfficiencyTable(os.path.join(PROJECT_ROOT, "tables", "detection_efficiency.tex"))
    table.table()
