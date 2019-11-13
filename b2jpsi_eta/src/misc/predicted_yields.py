""" Calculate predicted yields of B->J/psi eta events """
from __future__ import annotations

from constants.mode_info import mode2latex


# import pandas as pd


def predicted_info(decay: str) -> dict:
    """ Calculate predicted signal yield given 200e6 BB pairs, for decay
    :param decay: The decay mode you want information for
    :return: dict with the following keys:
    {num_bb: the number of BB pairs used in calculation,
     b2jpsieta: BF of B decay,
     jpsi: BF of J/psi decay,
     eta: BF of eta decay,
     det: Detection efficiency of mode,
     tot: product of all other keys,
     latex: LaTeX string of decay mode}
    """
    from constants import branching_ratios as br
    from efficiencies import detection

    num_bb = 200e6
    b2jpsieta = br.b02jpsi_eta[0]
    jpsi, eta = decay.split("_")
    jpsi = getattr(br, jpsi)[0]
    eta = getattr(br, eta)[0]
    det = detection.DetectionEfficiencyRow(decay).eff
    tot = num_bb * b2jpsieta * jpsi * eta * det

    info = dict(
        num_bb=num_bb, b2jpsieta=b2jpsieta, jpsi=jpsi, eta=eta, det=det, tot=tot, latex=f"${mode2latex[decay]}$"
    )
    return info


def table() -> pd.DataFrame:
    """Quick function to print and return a pandas DataFrame with predicted yield/BF information for all decay
    considered in this analysis."""
    import pandas as pd

    rows = [predicted_info(decay) for decay in mode2latex]
    df = pd.DataFrame(rows)
    print(df["latex tot".split()])
    return df


if __name__ == "__main__":
    table()
