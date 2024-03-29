#!/usr/bin/env python3
"""
Author: Kamil Slowikowski (Github: slowkow)

bsub.py

This script checks a Snakemake job's properties (threads, resources) and chooses
an appropriate LSF queue that meets the requirements. It also automatically
chooses the queue that is least busy unless you already specified a queue.

Usage
-----

Add 'threads' and 'resources' to your resource-intensive rules:

    rule my_rule:
        input: ...
        output ...
        threads: 4
        resources:
            mem = 8000                    # megabytes
            runtime = 35                  # minutes
            queue = 'my_favorite_queue'   # queue name

Invoke snakemake with the path to bsub.py:

    snakemake --jobs 999 --cluster "path/to/bsub.py -o bsub.stdout"

Consider adding bsub.py to a folder in your $PATH, so you can do:

    snakemake --jobs 999 --cluster "bsub.py -o bsub.stdout"

Note
----

You can use this script with Snakemake on the KEKCC cluster.

For your cluster at your institution, you'll have to modify this script.
"""

import argparse
import json
import os
import sys
from subprocess import check_output

from snakemake.utils import read_job_properties


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("jobscript")
    parser.add_argument("-e", help="Write bsub stderr here")
    parser.add_argument("-o", help="Write bsub stdout here")
    args = parser.parse_args()

    job_properties = read_job_properties(args.jobscript)

    # By default, we use 1 thread.
    threads = job_properties.get("threads", 1)

    # We'll leave unspecified the memory and runtime with 0 MB and 0 minutes.
    mem = int(job_properties["resources"].get("mem", "0"))
    runtime = int(job_properties["resources"].get("runtime", "0"))

    # Let the user specify the queue.
    queue = job_properties["resources"].get("queue", None)

    # Otherwise, choose an appropriate queue based on required resources.
    if not queue:
        queue = get_queue(threads, mem, runtime)

    # If we fail to find a queue, exit with an error.
    if not queue:
        msg = "No valid queue! job_properties:\n"
        js = json.dumps(job_properties, indent=4, sort_keys=True)
        sys.stderr.write(msg + js)
        sys.exit(1)

    # Submit the job to the queue.
    run_bsub(queue, threads, mem, runtime, args.jobscript, args.o, args.e)


def run_bsub(queue, threads, mem, runtime, script, stdout, stderr):
    cmd = "bsub -q {q} -n {t}".format(q=queue, t=threads)
    if mem:
        cmd += ' -R "rusage[mem={}]"'.format(mem)
    if runtime:
        cmd += " -W {}".format(runtime)
    if stdout:
        cmd += " -o {}".format(stdout)
    if stderr:
        cmd += " -e {}".format(stderr)
    cmd += " {s}".format(s=script)
    return os.system(cmd)


def get_queue(threads, mem, runtime):
    # Selected KEKCC queues
    queues = ["s", "l", "h", "sx", "lx", "hx"]

    # Find valid queues for this job's requirements.
    retval = []

    # Only consider 'vshort' if we specify a nonzero runtime.
    if threads == 1 and mem <= 1000 and 0 < runtime <= 15:
        retval.append("vshort")
    # The other queues are all ok if we leave runtime=0.
    if threads == 1 and mem <= 4000 and runtime <= 60:
        retval.append("short")
    if threads <= 4 and mem <= 8000 and runtime <= 60 * 24:
        retval.append("medium")
    if threads <= 6 and mem <= 8000 and runtime <= 60 * 24 * 3:
        retval.append("normal")
    if threads <= 4 and mem <= 8000 and runtime <= 60 * 24 * 7:
        retval.append("long")
    if threads <= 4 and mem <= 4000 and runtime <= 60 * 24 * 7 * 4:
        retval.append("vlong")
    if threads <= 6 and mem > 8000:
        retval.append("big")
    if 8 <= threads <= 16 and mem > 8000:
        retval.append("big-multi")
    # Make sure we have at least one valid queue.
    if not len(retval):
        return None
    # Get the number of currently running jobs on each queue.
    lines = check_output("bqueues").split(b"\n")[1:-1]
    lines = [line.decode("utf-8").split() for line in lines]
    njobs = {x[0]: int(x[7]) for x in lines}
    # Among valid queues, choose the one with fewest running jobs.
    return min(retval, key=lambda j: njobs[j])


if __name__ == "__main__":
    main()
