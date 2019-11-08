#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys

import basf2 as b2
import generators as ge
import modularAnalysis as ma


def submit_generation(n_events, dec_file, out_name, random_seed):
    # Command line args passed as strings, so ensure they're corrected to ints
    n_events = int(n_events)
    random_seed = int(random_seed)
    ge.set_random_seed(random_seed)
    my_path = b2.create_path()
    ma.setupEventInfo(noEvents=n_events, path=my_path)
    ge.add_evtgen_generator(path=my_path, finalstate="signal", signaldecfile=dec_file)
    ma.loadGearbox(path=my_path)
    my_path.add_module("RootOutput", outputFileName=out_name)
    b2.process(path=my_path)
    print(b2.statistics)


if __name__ == "__main__":
    args = sys.argv[1:]
    print(f"Generating events with arguments: {args}")
    submit_generation(*args)
    print("Done!")
