"""Simple exercises to get a feel for flavour tagger variables"""
from uncertainties import ufloat

FILENAME = (
    "/ghi/fs01/belle2/bdata/users/abudinen/flavorTagging/"
    "release-03-02-04MC12bnunubarTrain-JPsiKsDNNDataOptimizedNoCDCHits/Belle2_MC12_mixedb02all.root"
)
TREENAME = "variables"
OTHERFLAV = "mcFlavorOfOtherB0"  # Refactor after change to release 4
FT_VARS = "FBDT_qrCombined FANN_qrCombined DNN_qrCombined".split()
COLS = [OTHERFLAV] + FT_VARS + " isSignal PDG".split()
PRECUT = "isSignal && abs(FBDT_qrCombined) < 1.1"


def binomial_error(epsilon, N) -> float:
    """Calculate binomial error for a cut/rate"""
    from math import sqrt

    num = epsilon * (1 - epsilon)
    error = sqrt(num / N)
    return error


if __name__ == "__main__":
    import root_pandas
    from numpy import sign

    df = root_pandas.read_root(FILENAME, key=TREENAME, columns=COLS, where=PRECUT)
    true_flav = sign(df[OTHERFLAV])

    # Calculate wrong-tag fraction for each flavour tagger variable and add to dataframe
    for var in FT_VARS:
        df[f"wrongTag_{var}"] = true_flav != sign(df[var])

    df["mcFlavorOfSignalB0"] = sign(df["PDG"])
    df["sameFlavor"] = df["mcFlavorOfSignalB0"] == true_flav

    mix_prob_measured = df["sameFlavor"].mean()
    print(f"Observed mixing rate: {mix_prob_measured}\n")
    mix_prob_true = 0.1871
    misid_rate = (mix_prob_measured - mix_prob_true) / (1 - 2 * mix_prob_true)

    for var in FT_VARS:
        eff = df[f"wrongTag_{var}"].mean()
        err = binomial_error(eff, len(df))
        rate = ufloat(eff, err)
        print(f"Misid rate for {var}: {rate:.3f}")

    print(f"Misid rate from mixing prob: {misid_rate}")
