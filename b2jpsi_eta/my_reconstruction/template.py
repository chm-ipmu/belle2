import basf2 as b2
import modularAnalysis as ma
import variables.collections as vc
import variables.utils as vu
import vertex as vx
import yaml
from config.parse_config import DecayList


def reconstruction(input_file, output_file):
    my_path = b2.create_path()
    ma.inputMdst("default", input_file, my_path)

    # Find decay name from the input file name
    decay_name = "_".join(input_file.split("/")[-1].split("_")[0:2])

    # Load configuration file
    config = yaml.safe_load(open("config/reco_config.yaml"))
    options = config[decay_name]

    # Parse list of subdecays in decay chain
    decays = options["sub_decays"]
    decays = DecayList(decays)

    # Create particle lists for final state particles
    fsps = decays.get_fsps()
    for particle in fsps:
        ma.fillParticleList(particle, "", path=my_path)

    # Reconstruct requested decay chains
    for decay in decays:
        ma.reconstructDecay(str(decay), "", path=my_path)

    # Perform truth matching for requested particles
    truth_match_particles = decays.mothers
    for truth_match_particle in truth_match_particles:
        ma.looseMCTruth(truth_match_particle, path=my_path)

    # Perform vertex fitting
    head = decays.get_head()
    vtx_decay_string = decays.get_chain()
    print(vtx_decay_string)

    vx.vertexRave(head, 0, vtx_decay_string, constraint="iptube", path=my_path)

    # ma.rankByLowest("B0", 'chiProb', numBest=3, outputVariable='B_vtx_rank', path=my_path)
    # ma.variables.addAlias('B_vtx_rank', 'extraInfo(B_vtx_rank)')
    ma.buildRestOfEvent(head, path=my_path)

    # Tag-side
    vx.TagV(head, "breco", 0.001, path=my_path)

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

    trees = yaml.safe_load(open("config/tree_names.yaml"))
    for particle in decays.all_particles:
        ma.variablesToNtuple(
            particle,
            variables,
            filename=output_file,
            treename=trees[particle],
            path=my_path,
        )

    b2.process(my_path)
    print(b2.statistics)


if __name__ == "__main__":
    import sys

    args = sys.argv[1:]
    print(f"Reconstruction called with parameters: {args}")
    reconstruction(*args)
