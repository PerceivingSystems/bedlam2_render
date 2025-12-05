# SPDX-License-Identifier: GPL-2.0-or-later
# Copyright (c) 2025 Max Planck Society
#
# Convert SMPL-X animation in .npz format to .fbx animation with baked shapespace and without pose correctives
#
# Requirements:
#   + Blender 4.0.2+
#   + SMPL-X Blender add-on 20240206+ (UV_2023)
#
# Notes:
# + Running via command-line: blender --background --python smplx_anim_to_fbx.py -- --input /path/to/npz --output /path/to/fbx
#

import argparse
import bpy
from pathlib import Path
import sys
import time

##################################################
# Globals
##################################################
smplx_animation_path = Path("smplx_animation.npz")
output_path = Path("smplx_animation.fbx")

def convert_to_fbx(smplx_animation_path, output_path):
    if (not smplx_animation_path.exists()) or (smplx_animation_path.suffix != ".npz"):
        print(f"ERROR: Invalid input path: {smplx_animation_path}")
        return False

    if output_path.suffix != ".fbx":
        print(f"ERROR: Invalid output path: {output_path}")
        return False

    # Import animation, do not create keyframed pose correctives for faster import
    bpy.data.window_managers["WinMan"].smplx_tool.smplx_version = 'locked_head' # Use SMPL-X locked head (no head bun)
    bpy.data.window_managers["WinMan"].smplx_tool.smplx_uv = "UV_2023" # Use 2023 UV map

    anim_format="SMPL-X"

    bpy.ops.object.smplx_add_animation(filepath=str(smplx_animation_path), anim_format=anim_format, keyframe_corrective_pose_weights=False, target_framerate=30)

    # Export FBX with baked shape and without pose correctives
    output_path.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.object.smplx_export_fbx(filepath=str(output_path), export_shape_keys="NONE", target_format="UNREAL")
    return True

##############################################################################
# Main
##############################################################################
if __name__== "__main__":
    # Parse command-line arguments when invoked via `blender --background smplx_anim_to_fbx.py -- --input in.npz --output out.fbx`
    if bpy.app.background:
        if "--" in sys.argv:
            argv = sys.argv[sys.argv.index("--") + 1:]  # get all args after "--"

            parser = argparse.ArgumentParser(description="Convert SMPL-X animation in .npz format to FBX without pose correctives")

            parser.add_argument("--input", required=True, type=str, help="Path to .npz input file")
            parser.add_argument("--output", required=True, type=str, help="Path to .fbx output file")
            args = parser.parse_args(argv)
            smplx_animation_path = Path(args.input)
            output_path = Path(args.output)

    print(f"Converting: {smplx_animation_path} => {output_path}")
    start_time = time.perf_counter()
    convert_to_fbx(smplx_animation_path, output_path)
    print(f"  Finished. Time: {(time.perf_counter() - start_time):.1f}s")