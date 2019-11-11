import sys

import basf2 as b2
import mdst
import modularAnalysis as ma
import reconstruction as re

import simulation as si


def simulation(input_file, output_file):
    my_path = b2.create_path()
    print(f"Number of processes: {b2.get_nprocesses()}")

    # load input ROOT file
    ma.inputMdst(environmentType="default", filename=input_file, path=my_path)
    """
        Loads the specified ROOT (DST/mDST/muDST) files with the RootInput module.

        The correct environment (e.g. magnetic field settings) are determined from the specified environment type.
        The currently available environments are:

        - 'MC5': for analysis of Belle II MC samples produced with releases prior to build-2016-05-01.
          This environment sets the constant magnetic field (B = 1.5 T)
        - 'MC6': for analysis of Belle II MC samples produced with build-2016-05-01 or newer but prior to release-00-08-00
        - 'MC7': for analysis of Belle II MC samples produced with build-2016-05-01 or newer but prior to release-00-08-00
        - 'MC8', for analysis of Belle II MC samples produced with release-00-08-00 or newer but prior to release-02-00-00
        - 'MC9', for analysis of Belle II MC samples produced with release-00-08-00 or newer but prior to release-02-00-00
        - 'MC10', for analysis of Belle II MC samples produced with release-00-08-00 or newer but prior to release-02-00-00
        - 'default': for analysis of Belle II MC samples produced with releases with release-02-00-00 or newer.
          This environment sets the default magnetic field (see geometry settings)
        - 'Belle': for analysis of converted (or during of conversion of) Belle MC/DATA samples
        - 'None': for analysis of generator level information or during simulation/my_reconstruction of
          previously generated events

        Note that there is no difference between MC6 and MC7. Both are given for sake of completion.
        The same is true for MC8, MC9 and MC10

        Parameters:
            environmentType (str): type of the environment to be loaded
            filename (str): the name of the file to be loaded
            path (basf2.Path): modules are added to this path
            skipNEvents (int): N events of the input files are skipped
            entrySequences (list(str)): The number sequences (e.g. 23:42,101) defining
                the entries which are processed for each inputFileName.
            parentLevel (int): Number of generations of parent files (files used as input when creating a file) to be read
    """

    # In case of conflict with geometry, you may use this line instead:
    # analysis_main.add_module("RootInput", inputFileName='B2A101-Y4SEventGeneration-evtgen.root')

    # simulation
    si.add_simulation(path=my_path)

    # my_reconstruction
    re.add_reconstruction(path=my_path)

    # dump in MDST format
    mdst.add_mdst_output(path=my_path, mc=True, filename=output_file)

    # Show progress of processing
    progress = b2.register_module("ProgressBar")
    my_path.add_module(progress)

    # Process the events
    b2.process(my_path)
    print(b2.statistics)


if __name__ == "__main__":
    args = sys.argv[1:]
    print(f"Simulating Belle II and saving resultant MDST, with arguments: {args}")
    simulation(*args)
    print("Done!")
