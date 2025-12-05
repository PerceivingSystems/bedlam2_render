#!/usr/bin/env python3
# Copyright (c) 2025 Max Planck Society
# License: https://bedlam2.is.tuebingen.mpg.de/license.html
#
# Generate keyframed camera extrinsics/intrinsics from existing meta_exr_csv camera render ground truth.
# This is needed so that depth render pass (1 temporal sample) has correct camera pose when lookat/follow cameras were used.
# Temporal sample count affects the behavior of those low pass filters.
#

import csv
import json
from pathlib import Path
import sys

################################################################################

def load_camera_gt(camera_gt_path):
    csv_rows = []
    with open(camera_gt_path, mode="r") as csv_file:
        csv_reader = csv.DictReader(csv_file)
        csv_rows = list(csv_reader)

    return csv_rows


def generate_camera_animations(camera_animations_path, camera_gt_root, camera_animations_depth_path):

    camera_animations = {}
    with open(camera_animations_path, "r") as f:
        camera_animations = json.load(f)

    info_depth = { "config":{} }

    info_depth["config"]["sensor_width"] = camera_animations["info"]["config"]["sensor_width"]
    info_depth["config"]["sensor_height"] = camera_animations["info"]["config"]["sensor_height"]
    info_depth["config"]["static_world_location"] = False
    info_depth["config"]["follow"] = False
    info_depth["config"]["look_at"] = False

    camera_animations_depth = {}
    camera_animations_depth["info"] = info_depth

    for key in camera_animations:
        if key == "info":
            continue

        sequence_name = key

        camera_gt_path = camera_gt_root / f"{sequence_name}_camera.csv"
        csv_rows = load_camera_gt(camera_gt_path)

        # duplicate first and last item since we keyframe rendering at frame -1
        csv_rows.insert(0, csv_rows[0])
        csv_rows.append(csv_rows[-1])

        num_frames = len(csv_rows)

        keyframes = []
        for keyframe_index in range(num_frames):
            keyframe = {}
            keyframe["frame_index"] = -1 + keyframe_index # start at frame -1 for proper motion blur at frame 0
            keyframe["hfov"] = float(csv_rows[keyframe_index]["hfov"])

            # Camera is in world space so cameraroot must be at world space origin
            cameraroot = {}
            cameraroot["x"] = 0.0
            cameraroot["y"] = 0.0
            cameraroot["z"] = 0.0

            cameraroot["yaw"] = 0
            cameraroot["pitch"] = 0
            cameraroot["roll"] = 0
            keyframe["cameraroot"] = cameraroot

            camera_local_x = float(csv_rows[keyframe_index]["x"])
            camera_local_y = float(csv_rows[keyframe_index]["y"])
            camera_local_z = float(csv_rows[keyframe_index]["z"])
            camera_local_yaw = float(csv_rows[keyframe_index]["yaw"])
            camera_local_pitch = float(csv_rows[keyframe_index]["pitch"])
            camera_local_roll = float(csv_rows[keyframe_index]["roll"])

            keyframe["camera_local"] = { "x": camera_local_x, "y": camera_local_y, "z": camera_local_z, "yaw": camera_local_yaw, "pitch": camera_local_pitch, "roll": camera_local_roll }
            keyframe["type"] = "auto"

            keyframes.append(keyframe)

        camera_animations_depth[sequence_name] = { "keyframes": keyframes, "info": {} }

    print(f"Saving: {camera_animations_depth_path}")
    with open(camera_animations_depth_path, "w") as f:
        json.dump(camera_animations_depth, f, indent=4)

    return

def print_usage():
    print(f"Usage: {sys.argv[0]} RENDER_OUTPUT_DIRECTORY", file=sys.stderr)
    return

################################################################################
# Main
################################################################################

if len(sys.argv) != 2:
    print_usage()
    sys.exit(1)

render_output_root = Path(sys.argv[1])
camera_animations_path = render_output_root / "be_camera_animations.json"
camera_gt_root = render_output_root / "ground_truth" / "meta_exr_csv"
camera_animations_depth_path = render_output_root / "be_camera_animations_depth.json"

if not camera_animations_path.exists():
    print(f"ERROR: Camera animations definition not found: {camera_animations_path}", file=sys.stderr)
    sys.exit(1)

if not camera_gt_root.exists():
    print(f"ERROR: Camera ground truth files not found: {camera_gt_root}", file=sys.stderr)
    sys.exit(1)

generate_camera_animations(camera_animations_path, camera_gt_root, camera_animations_depth_path)

sys.exit(0)
