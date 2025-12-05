#!/usr/bin/env python3
# Copyright (c) 2025 Max Planck Society
# License: https://bedlam2.is.tuebingen.mpg.de/license.html
#
# Modify crowd sequence
#

import csv
import json
from math import sin, cos, tan, radians
import random
import re
import sys

from be_modify_sequences_config import *

################################################################################

def change_camera(csv_path, config_camera, config_type):

    c = config_camera

    with open(csv_path, "r") as f:
        bodies = f.readlines()

    output = []

    for line in bodies:
        line = line.rstrip()
        if line.startswith("Index"):
            output.append(line + "\n")
            continue
        else:
            items = line.split(",")
            index = int(items[0])
            rowtype = items[1]
            if index == 0:
                line = f"{line};cam_x_offset={c.x_offset_max};cam_y_offset={c.y_offset_max};cam_z_offset={c.z_offset_max};cam_yaw_min={c.yaw_min};cam_yaw_max={c.yaw_max};cam_pitch_min={c.pitch_min};cam_pitch_max={c.pitch_max};cam_roll_min={c.roll_min};cam_roll_max={c.roll_max};cam_config={config_type}"
                output.append(line + "\n")
                continue

            if rowtype == "Group":
                name = items[2]
                if c.override_cam_position:
                    x_start = c.x
                    y_start = c.y
                    if c.pitch_from_height:
                        z_start = random.uniform(c.z_min, c.z_max)
                    else:
                        z_start = c.z
                else:
                    x_start = float(items[3])
                    y_start = float(items[4])
                    z_start = float(items[5])

                x = x_start + random.uniform(-c.x_offset_max, c.x_offset_max)
                y = y_start + random.uniform(-c.y_offset_max, c.y_offset_max)
                z = z_start + random.uniform(-c.z_offset_max, c.z_offset_max)
                yaw = random.uniform(c.yaw_min, c.yaw_max)

                pitch_start = 0.0
                if c.pitch_from_height:
                    t = (z - c.z_min)/(c.z_max - c.z_min) # [0,1]
                    pitch_start = (1 - t) * c.pitch_z_min + t * c.pitch_z_max

                pitch = pitch_start + random.uniform(c.pitch_min, c.pitch_max)
                roll = random.uniform(c.roll_min, c.roll_max)
                comment = items[9]
                if c.hfov > 0:
                    # Use new horizontal field-of-view from configuration
                    match = re.search(r"(.+)camera_hfov=([^;]+)(.*)", comment)
                    if not match:
                        print("ERROR: Cannot find camera_hfov entry in source data")
                        sys.exit(1)

                    comment = match.group(1) + f"camera_hfov={c.hfov}" + match.group(3)

                line = f"{index},{rowtype},{name},{x},{y},{z},{yaw},{pitch},{roll},{comment}"

            output.append(line + "\n")

    csv_output_path = csv_path.parent / csv_path.name.replace(".csv", "_camrandom.csv")
    print(f"Saving modified sequence: {csv_output_path}")
    with open(csv_output_path, "w") as f:
        f.writelines(output)

    return

def change_camera_root(csv_path):

    with open(csv_path, "r") as f:
        bodies = f.readlines()

    output = []

    for line in bodies:
        line = line.rstrip()
        if line.startswith("Index"):
            output.append(line + "\n")
            continue

        items = line.split(",")
        index = int(items[0])
        rowtype = items[1]
        if index == 0:
            line = f"{line};cameraroot_yaw_min=0;cameraroot_yaw_max=360]"
            output.append(line + "\n")
            continue

        if rowtype == "Group":
            cam_root_yaw = random.uniform(0, 360)
            line = f"{line};cameraroot_yaw={cam_root_yaw}"

        output.append(line + "\n")

    csv_output_path = csv_path.parent / csv_path.name.replace(".csv", "_camroot.csv")
    print(f"Saving modified sequence: {csv_output_path}")
    with open(csv_output_path, "w") as f:
        f.writelines(output)

    return

# Rotate camera and bodies in world space (HDRI background and body lighting variation)
def change_sequence_root(csv_path, angle_min=0.0, angle_max=360.0):

    with open(csv_path, "r") as f:
        bodies = f.readlines()

    output = []

    angle = 0.0
    for line in bodies:
        line = line.rstrip()
        if line.startswith("Index"):
            output.append(line + "\n")
            continue
        else:
            items = line.split(",")

            index = int(items[0])
            rowtype = items[1]
            name = items[2]
            x = float(items[3])
            y = float(items[4])
            z = float(items[5])
            yaw  = float(items[6])
            pitch = float(items[7])
            roll = float(items[8])
            comment = items[9]


            if rowtype == "Group":
                angle = random.uniform(angle_min, angle_max)

                # Note: we do not need to rotate camera location since it's at origin for HDRI scenes

                yaw_r = yaw + angle
                if yaw_r >= 360.0:
                    yaw_r -= 360.0

                comment += f";angle={angle}"

                line = f"{index},{rowtype},{name},{x},{y},{z},{yaw_r},{pitch},{roll},{comment}"

            elif rowtype == "Body":
                # Rotate body in world space
                sin_a = sin(radians(angle))
                cos_a = cos(radians(angle))

                x_r = cos_a * x - sin_a * y
                y_r = sin_a * x + cos_a * y

                yaw_r = yaw + angle
                if yaw_r >= 360.0:
                    yaw_r -= 360.0

                line = f"{index},{rowtype},{name},{x_r},{y_r},{z},{yaw_r},{pitch},{roll},{comment}"

            output.append(line + "\n")

    csv_output_path = csv_path.parent / csv_path.name.replace(".csv", "_sequenceroot.csv")
    print(f"Saving modified sequence: {csv_output_path}")
    with open(csv_output_path, "w") as f:
        f.writelines(output)

    return

def change_autodistance(csv_path, config_camera, config_type):

    c = config_camera

    with open(csv_path, "r") as f:
        bodies = f.readlines()

    output = []

    hfov = -1
    for line in bodies:
        line = line.rstrip()
        if line.startswith("Index"):
            output.append(line + "\n")
            continue
        else:
            items = line.split(",")
            index = int(items[0])
            rowtype = items[1]
            name = items[2]
            x = float(items[3])
            y = float(items[4])
            z = float(items[5])
            yaw  = float(items[6])
            pitch = float(items[7])
            roll = float(items[8])
            comment = items[9]


            if index == 0:
                line = f"{line};cam_x_offset={c.x_offset_max};cam_y_offset={c.y_offset_max};cam_z_offset={c.z_offset_max};cam_yaw_min={c.yaw_min};cam_yaw_max={c.yaw_max};cam_pitch_min={c.pitch_min};cam_pitch_max={c.pitch_max};cam_roll_min={c.roll_min};cam_roll_max={c.roll_max};cam_config={config_type}"
                output.append(line + "\n")
                continue

            if rowtype == "Group":
                name = items[2]

                x = x + random.uniform(-c.x_offset_max, c.x_offset_max)
                y = y + random.uniform(-c.y_offset_max, c.y_offset_max)
                z = z + random.uniform(-c.z_offset_max, c.z_offset_max)
                yaw = random.uniform(c.yaw_min, c.yaw_max)
                pitch = random.uniform(c.pitch_min, c.pitch_max)
                roll = random.uniform(c.roll_min, c.roll_max)
                comment = items[9]

                # Randomize hfov
                hfov = random.uniform(c.hfov_min, c.hfov_max)
                if hfov < 0:
                    print(f"ERROR: Invalid hfov range specification for autodistance calculation: [{c.hfov_min}, {c.hfov_max}]")
                    sys.exit(1)

                # Use new horizontal field-of-view from configuration
                match = re.search(r"(.+)camera_hfov=([^;]+)(.*)", comment)
                if not match:
                    print("ERROR: Cannot find camera_hfov entry in source data")
                    sys.exit(1)

                comment = match.group(1) + f"camera_hfov={hfov}" + match.group(3)

                line = f"{index},{rowtype},{name},{x},{y},{z},{yaw},{pitch},{roll},{comment}"

            elif rowtype == "Body":

                # Camera distance from given hfov
                h_ref = c.camera_autodistance_ref # HFOV 52 needs at least 400cm distance from origin to fully see body, h_ref = 400 * tan (52/2) = 200
                alpha = radians(hfov/2)
                body_distance = h_ref / tan(alpha)

                x_autodistance = x + body_distance
                line = f"{index},{rowtype},{name},{x_autodistance},{y},{z},{yaw},{pitch},{roll},{comment}"

            output.append(line + "\n")

    csv_output_path = csv_path.parent / csv_path.name.replace(".csv", "_autodistance.csv")
    print(f"Saving modified sequence: {csv_output_path}")
    with open(csv_output_path, "w") as f:
        f.writelines(output)

    return

# Replace textured geometry clothing with clothing overlay
def clothing_overlay_replace(csv_path):

    with open(csv_path, "r") as f:
        bodies = f.readlines()

    output = []

    for line in bodies:
        line = line.rstrip()


        if line.startswith("Index"):
            output.append(line + "\n")
            continue

        items = line.split(",")
        index = int(items[0])
        rowtype = items[1]
        subject_animation_index = items[2].split("_")[-1]
        subject = items[2].replace(f"_{subject_animation_index}", "")
        if rowtype == "Body":
            match = re.search(r"(.+)texture_clothing=([^\;]+)(.*)", line)
            if match:
                texture_clothing_overlay = f"{subject}_{match.group(2)}"
                line = match.group(1) + f"texture_clothing_overlay={texture_clothing_overlay}" + match.group(3)

        output.append(line + "\n")

    csv_output_path = csv_path.parent / csv_path.name.replace(".csv", "_overlay.csv")
    print(f"Saving modified sequence: {csv_output_path}")
    with open(csv_output_path, "w") as f:
        f.writelines(output)

    return

# Add textured geometry clothing to files which do not have geometry clothing information
def clothing_overlay_add(csv_path):

    subject_gender = {}
    with open(SUBJECT_GENDER_PATH) as f:
        csv_reader = csv.DictReader(f)
        for row in csv_reader:
            subject_gender[row["Name"]] = row["Gender"]

    textures_overlay = {}
    with open(TEXTURES_OVERLAY_PATH) as f:
        textures_overlay = json.load(f)

    current_textures_overlay = { "f": [], "m": [] }

    with open(csv_path, "r") as f:
        bodies = f.readlines()

    output = []

    for line in bodies:
        line = line.rstrip()


        if line.startswith("Index"):
            output.append(line + "\n")
            continue

        items = line.split(",")
        index = int(items[0])
        rowtype = items[1]
        body = items[2]

        if rowtype == "Body":
            # rp_aaron_posed_002_1234
            match = re.search(r"(.+)_\d\d\d\d", body)
            if match:
                subject = match.group(1)
            else:
                subject = body.split("_")[0]

            if subject not in subject_gender:
                print(f"ERROR: Invalid subject name: {subject}, body name: {body}")
                sys.exit(1)

            gender = subject_gender[subject]
            if len(current_textures_overlay[gender]) == 0:
                current_textures_overlay[gender] = list(textures_overlay[gender])

            texture_clothing_overlay = current_textures_overlay[gender].pop(random.randrange(len(current_textures_overlay[gender])))

            line += f";texture_clothing_overlay={texture_clothing_overlay}"

        output.append(line + "\n")

    csv_output_path = csv_path.parent / csv_path.name.replace(".csv", "_overlay.csv")
    print(f"Saving modified sequence: {csv_output_path}")
    with open(csv_output_path, "w") as f:
        f.writelines(output)

    return

def print_usage():
    print(f"Usage: {sys.argv[0]} INPUTCSVPATH camera CONFIGTYPE", file=sys.stderr)
    print("       %s be_seq.csv camera cam_random_a" % (sys.argv[0]), file=sys.stderr)
    print(configs_camera.keys())
    print(f"Usage: {sys.argv[0]} INPUTCSVPATH cameraroot", file=sys.stderr)
    print(f"Usage: {sys.argv[0]} INPUTCSVPATH sequenceroot [angle_min angle_max]", file=sys.stderr)
    print(f"Usage: {sys.argv[0]} INPUTCSVPATH autodistance CONFIGTYPE", file=sys.stderr)
    print(f"Usage: {sys.argv[0]} INPUTCSVPATH clothing_overlay [add]", file=sys.stderr)
    print(f"Usage: {sys.argv[0]} INPUTCSVPATH hair", file=sys.stderr)
    return

################################################################################
# Main
################################################################################

if len(sys.argv) < 3:
    print_usage()
    sys.exit(1)

csv_path = Path(sys.argv[1])
target_type = sys.argv[2]

if target_type == "camera":
    config_type = sys.argv[3]
    if not config_type in configs_camera:
        print(f"ERROR: Undefined camera type: {config_type}", file=sys.stderr)
        print(configs_camera.keys())
        sys.exit(1)

    change_camera(csv_path, configs_camera[config_type], config_type)
elif target_type == "cameraroot":
    change_camera_root(csv_path)
elif target_type == "sequenceroot":
    if len(sys.argv) == 3:
        change_sequence_root(csv_path)
    else:
        angle_min = int(sys.argv[3])
        angle_max = int(sys.argv[4])
        change_sequence_root(csv_path, angle_min, angle_max)

elif target_type == "autodistance":
    config_type = sys.argv[3]
    if not config_type in configs_camera:
        print(f"ERROR: Undefined camera type: {config_type}", file=sys.stderr)
        print(configs_camera.keys())
        sys.exit(1)
    change_autodistance(csv_path, configs_camera[config_type], config_type)
elif target_type == "clothing_overlay":
    if len(sys.argv) == 4:
        clothing_overlay_add(csv_path)
    else:
        clothing_overlay_replace(csv_path)
else:
    print(f"ERROR: Unknown target type: {target_type}", file=sys.stderr)
    sys.exit(1)

sys.exit(0)
