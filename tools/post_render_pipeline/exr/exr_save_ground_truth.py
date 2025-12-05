#!/usr/bin/env python3
# Copyright (c) 2025 Max Planck Society
# License: https://bedlam2.is.tuebingen.mpg.de/license.html
#
# Save camera ground truth (JSON) from Unreal Movie Render Queue raw exr output file
#
# Requirements:
# + OpenEXR (1.3.9)
#   + Installation
#     + sudo apt install build-essential
#     + sudo apt install python3-dev
#     + sudo apt install libopenexr-dev
#     + pip install OpenEXR
#
# + OpenCV (4.7.0.72)
#   + PNG export
#   + Installation: pip install opencv-python-headless
#
# References:
#   + https://github.com/Psyop/Cryptomatte
#   + https://github.com/Synthesis-AI-Dev/exr-info
#

import OpenEXR
import Imath

import cv2
import json
from multiprocessing import Pool
import numpy as np
from pathlib import Path
import struct
import sys
import time

# Globals
DEFAULT_PROCESSES = 16

def process(input_exr, exr_type):
    output_dir = input_exr.parent.parent.parent
    exr = OpenEXR.InputFile(str(input_exr))

    meta_output_path = output_dir / "ground_truth" / exr_type / input_exr.parent.name / input_exr.name.replace(".exr", "_meta.json")
    status = process_meta(exr, meta_output_path)
    if not status:
        exr.close()
        return False

    exr.close()
    return True

def process_args(args):
    return process(*args)

def process_meta(exr, output_path):

    print("Extracting meta information")
    if (output_path.exists()):
        print(f"  Skipping. File exists: {output_path}")
        return True

    header = exr.header()

    meta = {}
    for key in header.keys():
        if key.startswith("unreal/"):
            if "ActorHitProxyMask" in key:
                continue

            meta[key] = header[key].decode()

    if len(meta) == 0:
        print(f"ERROR: No Unreal meta information found in EXR file")
        return False

    if not output_path.parent.exists():
        output_path.parent.mkdir(parents=True, exist_ok=True)

    print(f"  Exporting: {output_path}")
    with open(output_path, "w") as f:
        json.dump(meta, f, indent=4)

    return True

def print_usage():
    print("Usage: %s INPUT_EXR TYPE" % (sys.argv[0]), file=sys.stderr) # single file mode, input ends with .exr
    print("Usage: %s INPUT_EXR_DIR EXR_TYPE [NUM_PROCESSES]" % (sys.argv[0]), file=sys.stderr) # batch mode
    print("Usage: %s /path/to/render/exr_image meta_exr [NUM_PROCESSES]" % (sys.argv[0]), file=sys.stderr) # batch mode


################################################################################
# Main
################################################################################
if __name__ == "__main__":
    if (len(sys.argv) < 3) or (len(sys.argv) > 4):
        print_usage()
        sys.exit(1)

    input_exr = Path(sys.argv[1])
    exr_type = sys.argv[2]

    processes = DEFAULT_PROCESSES
    if len(sys.argv) >= 4:
        processes = int(sys.argv[3])

    batch_mode = False
    if input_exr.is_dir():
        batch_mode = True

    start_time = time.perf_counter()

    if not batch_mode:
        # Process single EXR file
        results = [process(input_exr, exr_type)]
    else:
        # Batch mode
        input_exr_files = sorted(input_exr.rglob("*.exr"))
        tasklist = []
        for input_exr_file in input_exr_files:
            tasklist.append( (input_exr_file, exr_type) )

        print(f"Starting pool with {processes} processes\n")
        pool = Pool(processes)
        results = pool.map(process_args, tasklist)

    if False not in results:
        print("EXR processing finished successfully.", file=sys.stderr)
        print(f"  Total conversion time: {(time.perf_counter() - start_time):.1f}s", file=sys.stderr)
    else:
        print("ERROR: EXR processing errors.", file=sys.stderr)
        sys.exit(1)
