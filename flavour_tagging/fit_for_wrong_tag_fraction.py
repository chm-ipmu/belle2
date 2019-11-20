"""Simultaneous fit to sign(PDF)*sign(FT_VAR) to measure wrong-tag fraction"""
import typing

import ROOT

FILENAME = (
    "/ghi/fs01/belle2/bdata/users/abudinen/flavorTagging/"
    "release-04-00-03TestSviatSel/Belle2_MC12_mixedb02all.root"
)
TREENAME = "variables"
PRECUT = "isSignal && abs(FBDT_qrCombined) < 1.1"
MIX_PROB_TRUE = 0.1871
mix_prob_true = ROOT.RooConstVar("mix_prob_true", "mix_prob_true", MIX_PROB_TRUE)


def fit_for_wrong_tag_fraction(ft_var: str = "mixFBDT") -> typing.Tuple[float, float]:
    """
    Use RooSimultaneous pdf to fit to product of PDG and flavour tagger variable ft_var
    :param ft_var: Flavour tagger variable you want to assess using fit
    :return: (measured value, error) of wrong-tag fraction
    """

    def make_name(name: str) -> typing.Tuple[str, str]:
        """Ensure a unique name for ROOT variables, in case this function is run in a loop during a single session."""
        name = f"{name}_{ft_var}"
        return name, name

    # Independent variable
    x = ROOT.RooRealVar(ft_var, ft_var, -2, 2)

    # Also need to create RooAbsReals for the cut variables, namely isSignal and FBDT_qrCombined
    var_isSignal = ROOT.RooRealVar("isSignal", "isSignal", -100, 100)
    var_FBDT_qrCombined = ROOT.RooRealVar(
        "FBDT_qrCombined", "FBDT_qrCombined", -100, 100
    )

    # This is what we want to measure using the fit -> must be floating
    start, mini, maxi = (
        0.25,
        -0.001,
        1.001,
    )  # Let it go slightly out of sensible limits (sometimes helps stability)
    wrong_tag_fraction = ROOT.RooRealVar(
        *make_name("wrong_tag_fraction"), start, mini, maxi
    )

    # Dilution factor is used in both SF and OF PDFs (see next block)
    dilution_formula = "(1 - 2*@0)*(1 - 2*@1)"  # 0: wrong-tag fraction, 1: physical B-mixing probability (constant)
    dilution_args = ROOT.RooArgList(wrong_tag_fraction, mix_prob_true)
    dilution = ROOT.RooFormulaVar(
        *make_name("dilution"), dilution_formula, dilution_args
    )

    # Formulas for PDFs  (SF = same flavour, OF = opposite flavour, referring to flavours of tag- and sig-B mesons)
    prob_SF_formula = "0.5 * (1 - @0)"
    prob_OF_formula = "0.5 * (1 + @0)"
    pdf_args = ROOT.RooArgList(dilution)
    prob_SF = ROOT.RooGenericPdf(*make_name("SF"), prob_SF_formula, pdf_args)
    prob_OF = ROOT.RooGenericPdf(*make_name("OF"), prob_OF_formula, pdf_args)

    # First need to reduce datasets by applying cut, so need RooDataSet with both fit variable and cut variables
    data_args = ROOT.RooArgSet(x, var_isSignal, var_FBDT_qrCombined)

    def create_category_dataset(name: str, cut: str) -> ROOT.RooDataSet:
        """Create a RooDataSet which contains the fitting variable and the variables we need for cuts."""
        ds = ROOT.RooDataSet(
            *make_name(name),
            data_args,
            ROOT.RooFit.ImportFromFile(FILENAME, TREENAME),
            ROOT.RooFit.Cut(cut),
        )
        return ds

    data_SF_all = create_category_dataset(
        "data_SF_all", cut=PRECUT + f" && {ft_var} > 0"
    )
    data_OF_all = create_category_dataset(
        "data_OF_all", cut=PRECUT + f" && {ft_var} < 0"
    )

    # Now create subset RooDataSet with just the fit variable, which can be used for RooSimultaneous
    x_set = ROOT.RooArgSet(x)
    data_sf = ROOT.RooDataSet(*make_name("sf"), data_SF_all, x_set)
    data_of = ROOT.RooDataSet(*make_name("of"), data_OF_all, x_set)

    # Create combined dataset / set-up for RooSimultaneous
    category = ROOT.RooCategory(*make_name("category"))
    # Categories are linked to PDFs in 1->1 mapping (1=SF, -1=OF)
    pdfs = {
        "1": prob_SF,
        "-1": prob_OF,
    }
    for flavour in pdfs:
        category.defineType(flavour)

    comb_data = ROOT.RooDataSet(
        *make_name("comb"),
        x_set,
        ROOT.RooFit.Index(category),
        ROOT.RooFit.Import("1", data_sf),
        ROOT.RooFit.Import("-1", data_of),
    )
    flavor_mix_prob = ROOT.RooSimultaneous(*make_name("flavor_mix_prob"), category)
    for flavour, pdf in pdfs.items():
        flavor_mix_prob.addPdf(pdf, flavour)

    # Perform fit
    result = flavor_mix_prob.fitTo(
        comb_data,
        ROOT.RooFit.Minos(False),
        ROOT.RooFit.Extended(False),
        ROOT.RooFit.Save(True),
    )
    result.Print()
    value = wrong_tag_fraction.getVal()
    error = wrong_tag_fraction.getError()
    return value, error


fit_for_wrong_tag_fraction("mixFANN")
