# Script for general reconstruction
import attr

import basf2 as b2
import modularAnalysis as ma
import variables.collections as vc
import variables.utils as vu
import vertex as vx


@attr.s
class Reconstruction:
    decay: str = attr.ib()
    path: b2.Path = attr.ib()

    def __attrs_post_init__(self) -> None:
        """
        Look at decay string given to constructor and instantiate a series of booleans to describe
        which total decay and sub-decays are involved in this decay mode.
        :return:  None
        """
        # Total decay
        self.is_jpsi2ee_eta2gammagamma = "jpsi2ee_eta2gammagamma" in self.decay
        self.is_jpsi2mumu_eta2gammagamma = "jpsi2mumu_eta2gammagamma" in self.decay
        self.is_jpsi2ee_eta2pipigamma = "jpsi2ee_eta2pipigamma" in self.decay
        self.is_jpsi2mumu_eta2pipigamma = "jpsi2mumu_eta2pipigamma" in self.decay
        self.is_jpsi2ee_eta2pipipi0 = "jpsi2ee_eta2pipipi0" in self.decay
        self.is_jpsi2mumu_eta2pipipi0 = "jpsi2mumu_eta2pipipi0" in self.decay
        self.is_jpsi2ee_eta23pi0 = "jpsi2ee_eta23pi0" in self.decay
        self.is_jpsi2mumu_eta23pi0 = "jpsi2mumu_eta23pi0" in self.decay

        # J/psi decays
        self.has_jpsi2ee = "jpsi2ee" in self.decay
        self.has_jpsi2mumu = "jpsi2mumu" in self.decay

        # eta decays
        self.has_eta2gammagamma = "eta2gammagamma" in self.decay
        self.has_eta2pipipi0 = "eta2pipipi0" in self.decay
        self.has_eta2pipigamma = "eta2pipigamma" in self.decay
        self.has_eta23pi0 = "eta23pi0" in self.decay

    def fill_particle_lists(self) -> None:
        """
        Depending on the decay mode considered, add particle lists of final state particles to path.
        For now, cuts are hard coded. (Could move to config file, or supply as an argument?)
        :return: None
        """
        # All decays have at least two gammas
        ma.fillParticleList("gamma", "E < 1.0", path=self.path)

        # J/psi decays
        if self.has_jpsi2ee:
            ma.fillParticleList(
                "e+", "electronID > 0.5 and abs(d0) < 1 and abs(z0) < 4", path=self.path
            )
        elif self.has_jpsi2mumu:
            ma.fillParticleList(
                "mu+", "muonID > 0.5 and abs(d0) < 1 and abs(z0) < 3", path=self.path
            )

        # eta decays
        if self.has_eta2pipigamma:
            ma.fillParticleList(
                "pi+", "chiProb > 0.001 and pionID > 0.1", path=self.path
            )

        elif self.has_eta2pipipi0:
            ma.fillParticleList(
                "pi+", "chiProb > 0.001 and pionID > 0.1", path=self.path
            )
            # ma.fillParticleList('pi0', '', path=self.path)

        elif self.has_eta2gammagamma:
            pass

        elif self.has_eta23pi0:
            # ma.fillParticleList('pi0', '', path=self.path)
            pass

    def reconstruct_jpsi_decay(self) -> None:
        """
        Reconstruct the J/psi part of the decay chain, depending on the decay mode considered.
        No cuts for now (second parameter), but will consider specifying them in a config file or passing them in as
        an argument.
        :return: None
        """
        if self.has_jpsi2ee:
            ma.reconstructDecay("J/psi -> e+ e-", "", path=self.path)
        elif self.has_jpsi2mumu:
            ma.reconstructDecay("J/psi -> mu+ mu-", "", path=self.path)

    def reconstruct_eta_decay(self) -> None:
        """
        Reconstruct the eta meson part of the decay chain, depending on the decay mode considered
        No cuts for now (second parameter), but will consider specifying them in a config file or passing them in as
        an argument.
        :return: None
        """
        if self.has_eta23pi0:
            ma.reconstructDecay("pi0 -> gamma gamma", "", path=self.path)
            ma.reconstructDecay("eta -> pi0 pi0 pi0", "", path=self.path)

        elif self.has_eta2pipipi0:
            ma.reconstructDecay("pi0 -> gamma gamma", "", path=self.path)
            ma.reconstructDecay("eta -> pi+ pi- pi0", "", path=self.path)

        elif self.has_eta2pipigamma:
            ma.reconstructDecay("eta -> pi+ pi- gamma", "", path=self.path)

        elif self.has_eta2gammagamma:
            ma.reconstructDecay("eta -> gamma gamma", "", path=self.path)

    def truth_match_all(self) -> None:
        """
        Perform modularAnalysis.looseMCTruth on each particle in the supplied decay mode.
        :return: None
        """
        particles = []

        # J/psi decays
        if self.has_jpsi2ee:
            particles.append("e+")
        elif self.has_jpsi2mumu:
            particles.append("mu+")

        # Eta decays
        if self.has_eta2gammagamma:
            particles.append("gamma")
        elif self.has_eta23pi0:
            particles.append("pi0")  # Is this needed? Does it cause an error?
            particles.append("gamma")
        elif self.has_eta2pipigamma:
            particles.append("pi+")
            particles.append("gamma")
        elif self.has_eta2pipipi0:
            particles.append("pi+")
            particles.append("pi0")  # Is this needed? Does it cause an error?
            particles.append("gamma")

        for particle in particles:
            ma.looseMCTruth(particle, path=self.path)

    @property
    def decay_string(self) -> str:
        """
        Correctly formatted decay string derived from the decay given to constructor. See constants/mode_info.py for
        more details
        :return: Decay string used for reconstruction
        """
        from constants.mode_info import mode2decay_string
        decay_string = mode2decay_string[self.decay]
        return decay_string

    def rave_vertex_reconstruction(
            self, list_name: str = "B0", conf_level: int = 0, constraint: str = "iptube"
    ) -> None:
        """
        Perform vertex reconstruction using Rave and the 'iptube' constraint. Could change the constraint to be an
        argument or specified in a config file.
        :return: None
        """
        vx.vertexRave(
            list_name,
            conf_level,
            self.decay_string,
            constraint=constraint,
            path=self.path,
        )

    def reconstruction(self, input_file: str, output_file: str) -> None:
        """
        A script to perform reconstruction as needed by the b2jpsi_eta analysis.
        :return: None
        """

        ma.inputMdst("default", input_file, self.path)

        # Create particle lists for final state particles
        self.fill_particle_lists()

        # Reconstruct decays in the given mode, by analysing input_file
        # J/psi decay
        self.reconstruct_jpsi_decay()
        # eta decay
        self.reconstruct_eta_decay()
        # They all have this one (you need to reconstruct the J/psi and eta first)
        b_meson_cuts = "isSignal and Mbc > 5.1 and Mbc < 5.4"  # Quite harsh for now, otherwise files too big.
        ma.reconstructDecay("B0 -> J/psi eta", b_meson_cuts, path=self.path)

        # For now truth match everything
        # All decays have these
        ma.looseMCTruth("B0", path=self.path)
        ma.looseMCTruth("J/psi", path=self.path)
        ma.looseMCTruth("eta", path=self.path)
        self.truth_match_all()

        self.rave_vertex_reconstruction()

        # ma.rankByLowest("B0", 'chiProb', numBest=3, outputVariable='B_vtx_rank', path=self.path)
        # ma.variables.addAlias('B_vtx_rank', 'extraInfo(B_vtx_rank)')
        ma.buildRestOfEvent("B0", path=self.path)

        # Tag-side
        vx.TagV("B0", "breco", 0.001, path=self.path)

        ma.buildEventKinematics(path=self.path)
        ma.buildEventShape(path=self.path)

        # Create centrmu-of-mass frame variables
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

        # These are in all decay modes
        # ma.variablesToNtuple(
        #     "J/psi", variables, filename=output_file, treename="jpsi", path=self.path
        # )
        # ma.variablesToNtuple(
        #     "eta", variables, filename=output_file, treename="eta", path=self.path
        # )
        ma.variablesToNtuple(
            "B0", variables, filename=output_file, treename="b0", path=self.path
        )
        # ma.variablesToNtuple(
        #     "gamma", variables, filename=output_file, treename="gamma", path=self.path
        # )

        # J/psi decays
        # if self.has_jpsi2ee:
        #     ma.variablesToNtuple(
        #         "e+",
        #         variables,
        #         filename=output_file,
        #         treename="electron",
        #         path=self.path,
        #     )
        #
        # elif self.has_jpsi2mumu:
        #     ma.variablesToNtuple(
        #         "mu+", variables, filename=output_file, treename="muon", path=self.path
        #     )
        #
        # # eta decays
        # if self.has_eta2pipigamma:
        #     ma.variablesToNtuple(
        #         "pi+", variables, filename=output_file, treename="pion", path=self.path
        #     )
        #
        # elif self.has_eta2pipipi0:
        #     ma.variablesToNtuple(
        #         "pi+", variables, filename=output_file, treename="pi", path=self.path
        #     )
        #     ma.variablesToNtuple(
        #         "pi0", variables, filename=output_file, treename="pi0", path=self.path
        #     )
        #
        # elif self.has_eta2gammagamma:
        #     pass
        #
        # elif self.has_eta23pi0:
        #     ma.variablesToNtuple(
        #         "pi0", variables, filename=output_file, treename="pi0", path=self.path
        #     )

        b2.process(self.path)
        print(b2.statistics)


# Quick testing ...
my_path = b2.create_path()
input_file = "../simulation/root_files/jpsi2ee_eta2gammagamma_0.root"
reco = Reconstruction(input_file, my_path)
reco.reconstruction(input_file, "test.root")


if __name__ == "__main__":
    import sys

    args = sys.argv[1:]

    print(f"Reconstruction called with parameters: {args}")

    input_file, output_file = args
    path = b2.create_path()

    reco = Reconstruction(decay=input_file, path=path)
    reco.reconstruction(input_file, output_file)

    print("Done!")
