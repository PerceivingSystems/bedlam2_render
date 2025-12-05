#!/usr/bin/env python3
# Copyright (c) 2025 Max Planck Society
# License: https://bedlam2.is.tuebingen.mpg.de/license.html
#
# Convert EXR json ground truth to csv format
# Uses unreal/camera data unless desired subframe is specified
#

import json
from pathlib import Path
import sys

def json_to_csv(data_root, sequence_path, exr_type, subframe=None):
    print(f"Converting to CSV: {sequence_path}")
    output = []
    output.append("name,x,y,z,yaw,pitch,roll,focal_length,sensor_width,sensor_height,hfov")

    json_paths = sorted(sequence_path.glob("*.json"))
    if len(json_paths) == 0:
        print("ERROR: no json files found", file=sys.stderr)
        return False

    cam_prefix_extrinsics = "unreal/camera"
    cam_prefix_intrinsics = "unreal/camera/FinalImage"

    if subframe is not None:
        cam_prefix_extrinsics = f"unreal/camera/bedlam/{subframe}"
        cam_prefix_intrinsics = cam_prefix_extrinsics

    for json_path in json_paths:
        with open(json_path, "r") as f:
            data = json.load(f)
            name = json_path.name.replace("_meta.json", ".png")
            x = data[f"{cam_prefix_extrinsics}/curPos/x"]
            y = data[f"{cam_prefix_extrinsics}/curPos/y"]
            z = data[f"{cam_prefix_extrinsics}/curPos/z"]
            yaw = data[f"{cam_prefix_extrinsics}/curRot/yaw"]
            pitch = data[f"{cam_prefix_extrinsics}/curRot/pitch"]
            roll = data[f"{cam_prefix_extrinsics}/curRot/roll"]
            focal_length = data[f"{cam_prefix_intrinsics}/focalLength"]
            sensor_width = data["unreal/camera/FinalImage/sensorWidth"]
            sensor_height = data["unreal/camera/FinalImage/sensorHeight"]
            hfov = data[f"{cam_prefix_intrinsics}/fov"]
            output.append(f"{name},{x},{y},{z},{yaw},{pitch},{roll},{focal_length},{sensor_width},{sensor_height},{hfov}")

    suffix = ""
    if subframe is not None:
        suffix = f"_{subframe}"

    output_root = data_root / "ground_truth" / f"{exr_type}_csv{suffix}"
    if not output_root.exists():
        output_root.mkdir(parents=True, exist_ok=True)

    output_path = output_root / f"{sequence_path.name}_camera{suffix}.csv"

    print(f"  Saving: {output_path}")
    with open(output_path, "w") as f:
        for line in output:
            f.write(f"{line}\n")

    return True

################################################################################
# Main
################################################################################
if __name__ == "__main__":
    if (len(sys.argv) < 2) or (len(sys.argv) > 4):
        print("Usage: %s RENDER_OUTPUT_DIRECTORY EXR_TYPE [subframe]" % (sys.argv[0]), file=sys.stderr)
        print("Usage: %s /path/to/render/output/dir meta_exr" % (sys.argv[0]), file=sys.stderr)
        print("Usage: %s /path/to/render/output/dir meta_exr subframe_6" % (sys.argv[0]), file=sys.stderr)
        sys.exit(1)

    data_root = Path(sys.argv[1])
    exr_type = sys.argv[2]
    subframe = None
    if len(sys.argv) >= 4:
        subframe = sys.argv[3]

    json_root = data_root / "ground_truth" / exr_type
    if not json_root.exists():
        print(f"ERROR: ground truth EXR json directory not found: {json_root}", file=sys.stderr)

    sequence_paths = sorted(json_root.glob("*"))

    for sequence_path in sequence_paths:
        status = json_to_csv(data_root, sequence_path, exr_type, subframe)
        if not status:
            sys.exit(1)

    sys.exit(0)
