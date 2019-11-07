# Script for general reconstruction

import basf2 as b2
import modularAnalysis as ma
import variables.collections as vc
import variables.utils as vu
import vertex as vx

from parse_decay import parse_decay


def fill_particle_lists(decay, path) -> None:
    """
    Depending on the decay mode considered, add particle lists of final state particles to path.
    For now, cuts are hard coded. (Could move to config file, or supply as an argument?)
    :param decay: enum specifying which subdecays are present in the decay mode, gained from using
    misc.parse_decay.parse_decay
    :param path: path to add particle lists to, gained from using basf2.create_path
    :return: None
    """
    # All decays have at least two gammas
    ma.fillParticleList('gamma', 'E < 1.0', path=path)

    if decay.has_jpsi2ee:
        ma.fillParticleList('e+', 'electronID > 0.5 and abs(d0) < 1 and abs(z0) < 4', path=path)

    elif decay.has_jpsi2mumu:
        print("HAS MUONS")
        ma.fillParticleList('mu+', 'muonID > 0.5 and abs(d0) < 1 and abs(z0) < 3', path=path)


def reconstruct_jpsi_decay(decay, path) -> None:
    """
    Reconstruct the J/psi part of the decay chain, depending on the decay mode considered.
    No cuts for now (second parameter), but will consider specifying them in a config file or passing them in as
    an argument.
    :param decay: enum specifying which subdecays are present in the decay mode, gained from using
    misc.parse_decay.parse_decay
    :param path: path to add particle lists to, gained from using basf2.create_path
    :return: None
    """
    if decay.has_jpsi2ee:
        ma.reconstructDecay('J/psi -> e+ e-', '', path=path)
    elif decay.has_jpsi2mumu:
        ma.reconstructDecay('J/psi -> mu+ mu-', '', path=path)


def reconstruct_eta_decay(decay, path) -> None:
    """
    Reconstruct the eta meson part of the decay chain, depending on the decay mode considered
    No cuts for now (second parameter), but will consider specifying them in a config file or passing them in as
    an argument.
    :param decay: enum specifying which subdecays are present in the decay mode, gained from using
    misc.parse_decay.parse_decay
    :param path: path to add particle lists to, gained from using basf2.create_path
    :return: None
    """
    if decay.has_eta23pi0:
        ma.reconstructDecay('eta -> pi0 pi0 pi0', '', path=path)
        ma.reconstructDecay('pi0 -> gamma gamma', '', path=path)

    elif decay.has_eta2pipipi0:
        ma.reconstructDecay('eta -> pi+ pi- pi0', '', path=path)
        ma.reconstructDecay('pi0 -> gamma gamma', '', path=path)

    elif decay.has_eta2pipigamma:
        ma.reconstructDecay('eta -> pi+ pi- gamma', '', path=path)

    elif decay.has_eta2gammagamma:
        ma.reconstructDecay('eta -> gamma gamma', '', path=path)


def truth_match_all(decay, path) -> None:
    """
    Perform modularAnalysis.looseMCTruth on each particle in the supplied decay mode.
    :param decay: enum specifying which subdecays are present in the decay mode, gained from using
    misc.parse_decay.parse_decay
    :param path: path to add particle lists to, gained from using basf2.create_path
    :return: None
    """
    particles = []

    # J/psi decays
    if decay.has_jpsi2ee:
        particles.append("e+")
    elif decay.has_jpsi2mumu:
        particles.append("mu+")

    # Eta decays
    if decay.has_eta2gammagamma:
        particles.append("gamma")
    elif decay.has_eta23pi0:
        particles.append("pi0")  # Is this needed? Does it cause an error?
        particles.append("gamma")
    elif decay.has_eta2pipigamma:
        particles.append("pi")
        particles.append("gamma")
    elif decay.has_eta2pipipi0:
        particles.append("pi")
        particles.append("pi0")  # Is this needed? Does it cause an error?
        particles.append("gamma")

    for particle in particles:
        ma.looseMCTruth(particle, path=path)


def rave_vertex_reconstruction(decay, path) -> None:
    """
    Perform vertex reconstruction using Rave and the 'iptube' constraint. Could change the constraint to be an
    argument or specified in a config file.
    :param decay: enum specifying which subdecays are present in the decay mode, gained from using
    misc.parse_decay.parse_decay
    :param path: path to add particle lists to, gained from using basf2.create_path
    :return: None
    """
    # J/psi decay is straightforward
    jpsi_decay_string = "J/psi -> ^{l}+ ^{l}+".format(l="e" if decay.has_jpsi2ee else "mu")

    # eta meson decay
    if decay.has_eta2gammagamma:
        eta_decay_string = "eta -> gamma gamma"
    elif decay.has_eta23pi0:
        eta_decay_string = "eta -> [pi0 -> gamma gamma] [pi0 -> gamma gamma] [pi0 -> gamma gamma]"
    elif decay.has_eta2pipigamma:
        eta_decay_string = "eta -> pi+ pi- gamma"
    elif decay.has_eta2pipipi0:
        eta_decay_string = "eta -> pi+ pi- [pi0 -> gamma gamma]"

    decay_string = f"B0 -> [{jpsi_decay_string}] [{eta_decay_string}]"

    vx.vertexRave('B0', 0, decay_string, constraint='iptube', path=path)


def reconstruction(input_file: str, output_file: str) -> None:
    """
    A script to perform reconstruction as needed by the b2jpsi_eta analysis.
    :param input_file: Location of a valid root file for the reconstruction to be performed on
    :param output_file: Location to save output root file after reconstruction performed
    :return: None
    """

    my_path = b2.create_path()
    ma.inputMdst('default', input_file, my_path)

    # Analyse input_file to see which subdecays are contained
    decay = parse_decay(input_file)

    # Create particle lists for final state particles
    fill_particle_lists(decay=decay, path=my_path)

    # Reconstruct decays in the given mode, by analysing input_file
    # J/psi decay
    reconstruct_jpsi_decay(decay=decay, path=my_path)
    # eta decay
    reconstruct_eta_decay(decay=decay, path=my_path)
    # They all have this one (you need to reconstruct the J/psi and eta first)
    ma.reconstructDecay('B0 -> J/psi eta', '', path=my_path)

    # For now truth match everything
    # All decays have these
    ma.looseMCTruth('B0', path=my_path)
    ma.looseMCTruth('J/psi', path=my_path)
    ma.looseMCTruth('eta', path=my_path)
    truth_match_all(decay=decay, path=my_path)

    rave_vertex_reconstruction(decay=decay, path=my_path)

    # ma.rankByLowest("B0", 'chiProb', numBest=3, outputVariable='B_vtx_rank', path=my_path)
    # ma.variables.addAlias('B_vtx_rank', 'extraInfo(B_vtx_rank)')
    ma.buildRestOfEvent("B0", path=my_path)

    # Tag-side
    vx.TagV('B0', 'breco', 0.001, path=my_path)

    ma.buildEventKinematics(path=my_path)
    ma.buildEventShape(path=my_path)

    # Create centrmu-of-mass frame variables
    cms_kinematics = vu.create_aliases(vc.kinematics, "useCMSFrame({variable})", prefix="CMS")

    variables = [item for sublist in [
        vc.kinematics,
        cms_kinematics,
        vc.deltae_mbc,
        vc.inv_mass,
        vc.event_shape,
        vc.vertex,
        vc.mc_truth,
        vc.mc_kinematics,
        vc.mc_vertex,
        vc.mc_tag_vertex,
    ] for item in sublist]

    # These are in all decay modes
    ma.variablesToNtuple('J/psi', variables, filename=output_file, treename="jpsi", path=my_path)
    ma.variablesToNtuple('eta', variables, filename=output_file, treename="eta", path=my_path)
    ma.variablesToNtuple('B0', variables, filename=output_file, treename="b0", path=my_path)
    ma.variablesToNtuple('gamma', variables, filename=output_file, treename="gamma", path=my_path)

    if decay.has_jpsi2ee:
        print("J/psi -> ee")
        ma.variablesToNtuple('e+', variables, filename=output_file, treename="electron", path=my_path)

    elif decay.has_jpsi2mumu:
        print("J/psi -> mumu")
        ma.variablesToNtuple('mu+', variables, filename=output_file, treename="muon", path=my_path)

    elif decay.has_eta2pipigamma:
        print("eta -> pipigamma")
        ma.variablesToNtuple('pi', variables, filename=output_file, treename="pion", path=my_path)

    elif decay.has_eta2pipipi0:
        print("eta -> pipipi0")
        ma.variablesToNtuple('pi', variables, filename=output_file, treename="pi", path=my_path)
        ma.variablesToNtuple('pi0', variables, filename=output_file, treename="pi0", path=my_path)

    elif decay.has_eta23pi0:
        print("eta -> 3pi0")
        ma.variablesToNtuple('pi0', variables, filename=output_file, treename="pi0", path=my_path)

    b2.process(my_path)
    print(b2.statistics)


if __name__ == '__main__':
    import sys

    args = sys.argv[1:]
    print(f'Reconstruction called with parameters: {args}')
    reconstruction(*args)
