#!/usr/bin/env python3
# Copyright (c) 2025 Max Planck Society
# License: https://bedlam2.is.tuebingen.mpg.de/license.html
#
# Saves animation folder NPZ files as T-pose NPZ (SMPL-X animation format, Y-up, one frame), one T-pose file per subject
#

import numpy as np
from pathlib import Path
import sys


################################################################################
# Main
################################################################################

def save_tpose_npz(input_path, output_path):
    with np.load(input_path, allow_pickle=True) as data:
        data_dict = dict(data)
        poses = data_dict["poses"][:1]
        poses[0][:] = 0.0
        data_dict["poses"] = poses

        trans = data_dict["trans"][:1]
        trans[0][:] = 0.0
        data_dict["trans"] = trans

        print(f"Saving: {output_path}")

        np.savez_compressed(output_path, **data_dict)

if len(sys.argv) != 3:
    print(f"Usage: {sys.argv[0]} INPUT_ROOT_PATH OUTPUT_ROOT_PATH", file=sys.stderr)
    print("       %s /path/to/input_animations/ /path/to/output_animations_tpose" % (sys.argv[0]), file=sys.stderr)
    sys.exit(1)

input_root = Path(sys.argv[1])
output_root = Path(sys.argv[2])

npz_paths = input_root.rglob("*.npz")
used_subjects = []
for npz_path in npz_paths:
    subject = None
    if npz_path.stem.startswith("moyo"):
        subject = "moyo"
    else:
        subject = npz_path.stem.rsplit("_", maxsplit=1)[0]

    if subject not in used_subjects:
        used_subjects.append(subject)
        output_path = output_root / f"{subject}_0000.npz"

        if not output_path.parent.exists():
            output_path.parent.mkdir(parents=True, exist_ok=True)
        save_tpose_npz(npz_path, output_path)
