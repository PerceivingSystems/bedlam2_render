#!/usr/bin/env python
# Copyright (c) 2025 Max Planck Society
# License: https://bedlam2.is.tuebingen.mpg.de/license.html
#
# Filter animations to only select the ones which exceed minimum frame count
#
import json
import numpy as np
from pathlib import Path
import sys

def get_animation_frames(npz_path):
#    print(f"Processing: {npz_path}", file=sys.stderr)
    num_frames = 0
    with np.load(npz_path) as data:
        num_frames = len(data["trans"])
    return num_frames

################################################################################
# Main
################################################################################

if len(sys.argv) != 4:
    print(f"Usage: {sys.argv[0]} /path/to/whitelist.json /path/to/npz/animations FRAMES_MIN")
    print(f"       {sys.argv[0]} /mnt/c/bedlam2/render/config/whitelist_animations_b2v3.json /mnt/c/bedlam2/animations/b2v3 300")
    sys.exit(1)

whitelist_path = Path(sys.argv[1])
animation_root = Path(sys.argv[2])
frames_min = int(sys.argv[3])

whitelist_frames = {}
body_animations = []
num_subjects = 0
num_animations = 0
with open(whitelist_path) as f:
    whitelist_animations = json.load(f)
    for subject in whitelist_animations:
        for animation_index in whitelist_animations[subject]:
            npz_path = animation_root / subject / animation_index / "motion_seq.npz"
            num_frames = get_animation_frames(npz_path)
            if num_frames < frames_min:
                continue

            # Add to output whitelist
            print(f"Adding: {subject}_{animation_index}, {num_frames}")
            if subject not in whitelist_frames:
                whitelist_frames[subject] = []
                num_subjects += 1

            whitelist_frames[subject].append(animation_index)
            num_animations += 1

print(f"Filtered subjects: {num_subjects}")
print(f"Filtered animations: {num_animations}")

target_path = Path(".") / f"whitelist_animations_frames_{frames_min}.json"
print(f"Saving: {target_path}")
with open(target_path, "w") as json_file:
    json.dump(whitelist_frames, json_file, indent=4)

sys.exit(0)