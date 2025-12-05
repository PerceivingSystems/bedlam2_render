#!/usr/bin/env python
# SPDX-License-Identifier: GPL-2.0-or-later
# Copyright (c) 2025 Max Planck Society
#
# Convert SMPL-X animation in .npz format to .fbx animation with baked shapespace and without pose correctives.
#
# Requirements:
#   + Blender 4.0.2+
#   + SMPL-X Blender add-on 20240206+ (UV_2023)
#
# Notes:
# + Python for Windows
#   py -3 smplx_anim_to_fbx_batch.py \path\to\input\dir \path\to\output\dir 12
#

from multiprocessing import Pool
from pathlib import Path
import subprocess
import sys
import time

# Globals
BLENDER_APP_PATH = r"C:\apps\blender-4.0.2-windows-x64\blender.exe"
DEFAULT_PROCESSES = 12

def worker(blender_app_path, input, output):
    # $BLENDERPATH --background --python smplx_anim_to_fbx.py -- --input "$INPUT" --output "$OUTPUT"
    subprocess_args = [blender_app_path, "--background", "--python", "smplx_anim_to_fbx.py", "--"]
    subprocess_args.extend(["--input", input])
    subprocess_args.extend(["--output", output])
    subprocess.run(subprocess_args)
    return True

def worker_args(args):
    return worker(*args)

################################################################################
# Main
################################################################################
if __name__ == "__main__":
    if (len(sys.argv) < 3) or (len(sys.argv) > 4):
        print('Usage: %s INPUTDIR OUTPUTDIR [PROCESSES]' % (sys.argv[0]), file=sys.stderr)
        sys.exit(1)

    input_dir = Path(sys.argv[1])
    output_dir = Path(sys.argv[2])

    if len(sys.argv) == 4:
        processes = int(sys.argv[3])
    else:
        processes = DEFAULT_PROCESSES

    # Get list of source target files and sort by name
    filenames = sorted(input_dir.rglob("*.npz"))

    num_files = len(filenames)

    print(f"Found .npz files: {num_files}")
    print(f"Starting pool with {processes} processes\n", file=sys.stderr)
    pool = Pool(processes)

    start_time = time.perf_counter()
    tasklist = []
    for input_path in filenames:

        if input_path.name.startswith("moyo"):
            output_path = output_dir / "moyo" / f"{input_path.stem}.fbx"
        else:
            # it_4001_XL_2400.npz
            body_name = input_path.name.rsplit("_", maxsplit=1)[0]
            output_path = output_dir / body_name / f"{input_path.stem}.fbx"

        tasklist.append( (BLENDER_APP_PATH, str(input_path), str(output_path)) )

    result = pool.map(worker_args, tasklist)
    print(f"Finished. Total batch conversion time: {(time.perf_counter() - start_time):.1f}s")
