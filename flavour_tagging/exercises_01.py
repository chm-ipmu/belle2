"""Simple exercises to get a feel for flavour tagger variables"""
from uncertainties import ufloat

FILENAME = (
    "/ghi/fs01/belle2/bdata/users/abudinen/flavorTagging/"
    "release-04-00-03TestSviatSel/Belle2_MC12_mixedb02all.root"
)
TREENAME = "variables"
OTHERFLAV = "mcFlavorOfOtherB"
FT_VARS = "FBDT_qrCombined FANN_qrCombined DNN_qrCombined".split()
COLS = [OTHERFLAV] + FT_VARS + " isSignal PDG".split()
PRECUT = "isSignal && abs(FBDT_qrCombined) < 1.1"
MIX_PROB_TRUE = 0.1871


def binomial_error(epsilon, N) -> float:
    """
    Calculate binomial error of efficiency epsilon from total number N.
    :param epsilon: Efficiency of a given cut
    :param N: Number of entries before cut
    :return: calculate binomial error
    """
    from math import sqrt

    num = epsilon * (1 - epsilon)
    error = sqrt(num / N)
    return error


def get_mean_with_error(series):
    """Calculate efficiency/rate of a series and corresponding binomial error. Assumes series of 0s and 1s."""
    efficiency = series.mean()
    error = binomial_error(efficiency, len(series))
    return ufloat(efficiency, error)


if __name__ == "__main__":
    import root_pandas
    from numpy import sign

    df = root_pandas.read_root(FILENAME, key=TREENAME, columns=COLS, where=PRECUT)
    true_flav = sign(df[OTHERFLAV])
    df["mcFlavorOfSignalB0"] = sign(df.PDG)
    df["sameFlavor"] = df.mcFlavorOfSignalB0 == true_flav

    # Calculate wrong-tag fraction for each flavour tagger variable and add to dataframe
    for var in FT_VARS:
        # Flavor of tag-B from flavour tagger variable. This could be right or wrong, depending on true flavour of the B
        tagged_flav = sign(df[var])
        # Wrong tag is when tagged flavour doesn't agree with true flavour from MC truth
        df[f"wrongTag_{var}"] = true_flav != tagged_flav
        # tag-B / sig-B can oscillate to become same flavour, modulo errors from flavour tagging
        df[f"sameFlavor_{var}"] = df.mcFlavorOfSignalB0 == tagged_flav


    def calc_wrong_tag_fraction(measured_mixing, true_mixing=MIX_PROB_TRUE):
        """
        Calculate the wrong-tag fraction from formula using mixing probability of B meson.
        :param measured_mixing: The observed mixing prob., which differs from true mixing prob. due to incorrect flavour tags
        :param true_mixing: The true probability of B mixing, default is MIX_PROB_TRUE
        :return: calculated wrong-tag fraction
        """
        delta = measured_mixing - true_mixing
        dilution = 1 - 2 * true_mixing
        wrong_tag_fraction = delta / dilution
        return wrong_tag_fraction


    mix_prob_from_mc_truth = get_mean_with_error(df.sameFlavor)
    print(f"Mixing rate (from MC truth): {mix_prob_from_mc_truth}\n")
    # wrong_tag_fraction_from_mc_truth = calc_wrong_tag_fraction(
    #     measured_mixing=mix_prob_from_mc_truth
    # )

    print("~~~ Wrong-tag fraction ~~~")

    for var in FT_VARS:
        wrong_tag_count = get_mean_with_error(df[f"wrongTag_{var}"])
        measured_mixing = get_mean_with_error(df[f"sameFlavor_{var}"])
        wrong_tag_mix = calc_wrong_tag_fraction(measured_mixing=measured_mixing)
        wrong_tag_mix_mc = calc_wrong_tag_fraction(
            measured_mixing=measured_mixing, true_mixing=mix_prob_from_mc_truth
        )
        # Values with uncertainties are consistent if their difference is consistent with zero
        # diff = abs(wrong_tag_count - wrong_tag_mix)
        # consistent = (diff.nominal_value - diff.std_dev) <= 0

        print("-", var)
        print(f"\tCount          : {wrong_tag_count:.3f}")
        print(f"\tMix (true)     : {wrong_tag_mix:.3f}")
        print(f"\tMix (MC)       : {wrong_tag_mix_mc:.3f}")
        print(f"\tCount - Mix    : {abs(wrong_tag_count - wrong_tag_mix):.3f}")
        print(f"\tCount - Mix MC : {abs(wrong_tag_count - wrong_tag_mix_mc):.3f}")
        # print(f"\tConsistent? {consistent}\n")
