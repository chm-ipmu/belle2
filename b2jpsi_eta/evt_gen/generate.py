#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys

import basf2 as b2
import generators as ge
import modularAnalysis as ma

TOTAL_GEN = int(1e6)
N_GEN = int(1e5)
N_JOBS = int(TOTAL_GEN / N_GEN)
THIS_FILE = "/home/belle2/murphyco/PycharmProjects/belle2/b2jpsi_eta/evt_gen/generate.py"


def submit_generation(n_events, dec_file, out_name, random_seed):
    # Command line args passed as strings, so ensure they're corrected to ints
    n_events = int(n_events)
    random_seed = int(random_seed)
    ge.set_random_seed(random_seed)
    # out_name = f"{out_name}_{random_seed}.root"   # No longer needed thanks to snakemake
    my_path = b2.create_path()
    ma.setupEventInfo(noEvents=n_events, path=my_path)
    ge.add_evtgen_generator(
        path=my_path,
        finalstate='signal',
        signaldecfile=dec_file
    )
    ma.loadGearbox(path=my_path)
    my_path.add_module('RootOutput', outputFileName=out_name)
    b2.process(path=my_path)
    print(b2.statistics)


# No longer needed thanks to Snakemake
# def submit_all():
#     # Generate .root files for all DEC files in DEC_FILES directory
#     files = os.listdir(DEC_FILES)
#     files = [os.path.join(DEC_FILES, x) for x in files]   # Recover full path
#     seeds = list(range(N_JOBS))   # Ensure unique events generated
#
#     # Generate output filename from input filename (.root added in generation function)
#     def dec2root(string):
#         string = string.replace("dec_files", "root_files")
#         string = string.replace(".DEC", "")
#         return string
#
#     # Build list of command line arguments to send to bsub
#     arg_sets = [
#         [str(N_GEN), file, dec2root(file), str(seed)]
#         for file, seed in product(files, seeds)
#     ]
#
#     # Create bsub command in a unique .sh file and submit
#     for i, arg_set in enumerate(arg_sets):
#         args = " ".join(arg_set)
#         command = f"python3 {THIS_FILE} {args}"
#         print(f"{command}\n")
#         fname = f"sub_{i}.sh"
#         with open(fname, "w") as f:
#             f.write(command)
#         subprocess.call(["chmod", "+x", fname])
#         subprocess.call(["bsub", f"./{fname}"])


if __name__ == '__main__':
    args = sys.argv[1:]
    # if args[0] == "submit_all":
    #     submit_all()
    # else:
    print(f"Generating events with arguments: {args}")
    submit_generation(*args)
    print("Done!")
