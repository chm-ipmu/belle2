# Script to reconstruct:
## B -> J/psi eta
### J/psi -> ee
### eta -> pi pi pi

import basf2 as b2
import modularAnalysis as ma
import variables.collections as vc
import variables.utils as vu
import vertex as vx


def reconstruction(input_file, output_file):

    my_path = b2.create_path()
    ma.inputMdst("default", input_file, my_path)

    ma.fillParticleList(
        "e+", "electronID > 0.5 and abs(d0) < 1 and abs(z0) < 4", path=my_path
    )
    ma.fillParticleList("gamma", "E < 1.0", path=my_path)

    ma.reconstructDecay("J/psi -> e+ e-", "", path=my_path)
    ma.reconstructDecay("pi0 -> gamma gamma", "", path=my_path)
    ma.reconstructDecay("eta -> pi0 pi0 pi0", "", path=my_path)
    ma.reconstructDecay("B0 -> J/psi eta", "", path=my_path)

    ma.looseMCTruth("J/psi", path=my_path)
    ma.looseMCTruth("pi0", path=my_path)
    ma.looseMCTruth("eta", path=my_path)
    ma.looseMCTruth("B0", path=my_path)

    vx.vertexRave(
        "B0",
        0,
        "B0 -> [J/psi -> ^e+ ^e-] [eta -> [pi0 -> gamma gamma] [pi0 -> gamma gamma] [pi0 -> gamma gamma]]",
        constraint="iptube",
        path=my_path,
    )

    # ma.rankByLowest("B0", 'chiProb', numBest=3, outputVariable='B_vtx_rank', path=my_path)
    # ma.variables.addAlias('B_vtx_rank', 'extraInfo(B_vtx_rank)')
    ma.buildRestOfEvent("B0", path=my_path)

    # Tag-side
    vx.TagV("B0", "breco", 0.001, path=my_path)

    ma.buildEventKinematics(path=my_path)
    ma.buildEventShape(path=my_path)

    # Create centre-of-mass frame variables
    cms_kinematics = vu.create_aliases(
        vc.kinematics, "useCMSFrame({variable})", prefix="CMS"
    )

    variables = [
        item
        for sublist in [
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
        ]
        for item in sublist
    ]

    ma.variablesToNtuple(
        "e+", variables, filename=output_file, treename="electron", path=my_path
    )
    ma.variablesToNtuple(
        "J/psi", variables, filename=output_file, treename="jpsi", path=my_path
    )
    ma.variablesToNtuple(
        "eta", variables, filename=output_file, treename="eta", path=my_path
    )
    ma.variablesToNtuple(
        "B0", variables, filename=output_file, treename="b0", path=my_path
    )

    b2.process(my_path)
    print(b2.statistics)


if __name__ == "__main__":
    import sys

    args = sys.argv[1:]
    print(f"Reconstruction called with parameters: {args}")
    reconstruction(*args)
