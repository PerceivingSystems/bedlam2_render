#!/usr/bin/env python3
# Copyright (c) 2025 Max Planck Society
# License: https://bedlam2.is.tuebingen.mpg.de/license.html
#
# Generate keyframes for camera movement during sequence
#

import csv
import json
from math import sin, cos, tan, radians, atan, degrees
from pathlib import Path
import random
import sys

from be_generate_camera_animations_config import *

################################################################################

def read_csv(csv_path):
    sequences = {}

    with open(csv_path, mode="r") as csv_file:
        csv_reader = csv.DictReader(csv_file)
        csv_rows = list(csv_reader)

        use_body = False
        sequence_name = None

        for row in csv_rows:
            sequence_frames = 0
            camera_hfov = 0.0
            cameraroot_x = 0.0
            cameraroot_y = 0.0
            cameraroot_z = 0.0
            cameraroot_yaw = 0.0
            ground_height_world = 0.0

            if row["Type"] == "Body":
                if use_body:
                    body = row["Body"]
                    yaw = float(row["Yaw"])
                    sequence = sequences[sequence_name]
                    sequence["body"] = body
                    sequence["body_yaw"] = yaw
                    use_body = False # record only first body

            if row["Type"] == "Group":
                # Parse group configuration
                values = row["Comment"].split(";")
                dict_keys = []
                dict_values = []
                for value in values:
                    dict_keys.append(value.split("=")[0])
                    dict_values.append(value.split("=")[1])
                group_config = dict(zip(dict_keys, dict_values))

                sequence_name = group_config["sequence_name"]
                sequence_frames = int(group_config["frames"])
                camera_hfov = float(group_config["camera_hfov"])

                if "cameraroot_x" in group_config:
                    cameraroot_x = float(group_config["cameraroot_x"])
                    cameraroot_y = float(group_config["cameraroot_y"])
                    cameraroot_z = float(group_config["cameraroot_z"])

                if "cameraroot_yaw" in group_config:
                    cameraroot_yaw = float(group_config["cameraroot_yaw"])

                if "ground_height_world" in group_config:
                    ground_height_world = float(group_config["ground_height_world"])

                sequence = {}
                sequence["frames"] = sequence_frames
                sequence["hfov"] = camera_hfov
                sequence["cameraroot"] = { "x": cameraroot_x, "y": cameraroot_y, "z": cameraroot_z, "yaw": cameraroot_yaw }
                sequence["ground_height_world"] = ground_height_world
                x = float(row["X"])
                y = float(row["Y"])
                z = float(row["Z"])
                yaw = float(row["Yaw"])
                pitch = float(row["Pitch"])
                roll = float(row["Roll"])
                sequence["camera"] = { "x": x, "y": y, "z": z, "yaw": yaw, "pitch": pitch, "roll": roll }

                camera_range_max = -1.0
                if "camera_radius_max" in group_config:
                    camera_range_max = float(group_config["camera_radius_max"])
                sequence["camera_radius_max"] = camera_range_max

                camera_height_min = -1.0
                if "camera_height_min" in group_config:
                    camera_height_min = float(group_config["camera_height_min"])
                sequence["camera_height_min"] = camera_height_min

                camera_height_max = -1.0
                if "camera_height_max" in group_config:
                    camera_height_max = float(group_config["camera_height_max"])
                sequence["camera_height_max"] = camera_height_max

                if "theta_min" in group_config:
                    theta_min = float(group_config["theta_min"])
                    sequence["theta_min"] = theta_min
                    theta_max = float(group_config["theta_max"])
                    sequence["theta_max"] = theta_max

                sequences[sequence_name] = sequence

                use_body = True # log data of first body

    return sequences

def get_random_location(config, last_distance=None, last_theta=None, last_phi=None, last_camera_local_y=None, last_camera_local_z=None):
    c = config
    if last_distance is None:
        distance = random.uniform(c.distance_min, c.distance_max)

        theta_min = None
        theta_max = None
        if len(c.theta_ranges) == 0:
            theta_min = c.theta_min
            theta_max = c.theta_max
        else:
            (theta_min, theta_max) = random.choice(c.theta_ranges)
        theta = random.uniform(theta_min, theta_max)

        phi = random.uniform(c.phi_min, c.phi_max)
        camera_local_y = random.uniform(c.camera_local_y_min, c.camera_local_y_max)
        camera_local_z = random.uniform(c.camera_local_z_min, c.camera_local_z_max)
    else:

        valid_distance = False
        while not valid_distance:
            delta = random.uniform(c.distance_mindelta, c.distance_maxdelta) * random.choice([-1.0, 1.0])

            distance = last_distance + delta
            if c.distance_min <= distance <= c.distance_max:
                valid_distance = True

        delta = random.uniform(c.theta_mindelta, c.theta_maxdelta) * random.choice([-1.0, 1.0])
        theta = last_theta + delta

        valid_phi = False
        while not valid_phi:
            delta = random.uniform(c.phi_mindelta, c.phi_maxdelta) * random.choice([-1.0, 1.0])
            phi = last_phi + delta
            if c.phi_min <= phi <= c.phi_max:
                valid_phi = True

        valid_camera_local_y = False
        while not valid_camera_local_y:
            delta = random.uniform(c.camera_local_y_mindelta, c.camera_local_y_maxdelta) * random.choice([-1.0, 1.0])
            camera_local_y = last_camera_local_y + delta
            if c.camera_local_y_min <= camera_local_y <= c.camera_local_y_max:
                valid_camera_local_y = True

        valid_camera_local_z = False
        while not valid_camera_local_z:
            delta = random.uniform(c.camera_local_z_mindelta, c.camera_local_z_maxdelta) * random.choice([-1.0, 1.0])
            camera_local_z = last_camera_local_z + delta
            if c.camera_local_z_min <= camera_local_z <= c.camera_local_z_max:
                valid_camera_local_z = True

    return (distance, theta, phi, camera_local_y, camera_local_z)

def get_random_hfov(config, last_hfov=None):
    c = config
    (hfov_min, hfov_max) = c.hfov_ranges[0]

    if last_hfov is None:
        hfov = random.uniform(hfov_min, hfov_max)
    else:
        valid_hfov = False
        while not valid_hfov:
            delta = random.uniform(c.hfov_mindelta, c.hfov_maxdelta) * random.choice([-1.0, 1.0])

            hfov = last_hfov + delta
            if hfov_min <= hfov <= hfov_max:
                valid_hfov = True

    return hfov


def get_vcam_keyframes(config, sequence, hfov, body_yaw, vcam_focallength, vcam_capture, info):
    c = config
    data_json = None
    vcam_path = VCAM_ROOT / c.vcam_type[0] / c.vcam_type[1] / vcam_focallength / vcam_capture # Example: C:\bedlam2\render\config\vcam\stand\landscape\14\vcam_stand_20240723_0014.json

    num_frames = sequence["frames"] + 2 # motion blur requires extra keyframes at beginning and end
    extrinsics = []
    with open(vcam_path, "r") as f:
        data_json = json.load(f)

        extrinsics = data_json["extrinsics"]

        # Trim off frames at start and end of raw captures
        extrinsics = extrinsics[VCAM_TRIM_FRAMES:-VCAM_TRIM_FRAMES]

        if c.vcam_reverse:
            extrinsics.reverse()

        # Sample sublist of length num_frames from extrinsics
        start_index_max = len(extrinsics) - num_frames
        start_index = random.randint(0, start_index_max)
        end_index = start_index + num_frames
        extrinsics = extrinsics[start_index:end_index]

    sequence_body = sequence["body"]
    sequence_body_yaw = sequence["body_yaw"]

    cameraroot_yaw = 0.0
    if c.vcam_theta_front:
        body_yaw_offset = -body_yaw[sequence_body] # convert right-hand rule yaw to Unreal left-hand rule yaw
        # Unreal default body is facing positive Y axis, camera is along negative X axis
        # -90 yaw rotates cameraroot so that camera is looking along negative Y axis
        cameraroot_yaw = -90.0 + sequence_body_yaw + body_yaw_offset


    # Handle optional theta range overrides
    if "theta_min" in sequence:
        theta_min = sequence["theta_min"]
        theta_max = sequence["theta_max"]
        c = c._replace(theta_min = theta_min)
        c = c._replace(theta_max = theta_max)

    theta_min = None
    theta_max = None
    if len(c.theta_ranges) == 0:
        theta_min = c.theta_min
        theta_max = c.theta_max
    else:
        (theta_min, theta_max) = random.choice(c.theta_ranges)
    theta = random.uniform(theta_min, theta_max)

    info["theta"] = theta
    cameraroot_yaw += theta

    vcam_height_offset = random.uniform(c.vcam_height_offset_min, c.vcam_height_offset_max)
    info["vcam_height_offset"] = vcam_height_offset

    vcam_x_offset = random.uniform(c.vcam_x_offset_min, c.vcam_x_offset_max)
    info["vcam_x_offset"] = vcam_x_offset

    vcam_pitch_offset = random.uniform(c.vcam_pitch_offset_min, c.vcam_pitch_offset_max)
    info["vcam_pitch_offset"] = vcam_pitch_offset

    keyframes = []

    for keyframe_index in range(num_frames):
        keyframe = {}
        keyframe["frame_index"] = -1 + keyframe_index # start at frame -1 for proper motion blur at frame 0
        keyframe["hfov"] = hfov

        # Place cameraroot at desired height above ground
        cameraroot = {}
        cameraroot["x"] = sequence["cameraroot"]["x"]
        cameraroot["y"] = sequence["cameraroot"]["y"]
        cameraroot["z"] = sequence["cameraroot"]["z"]

        cameraroot["yaw"] = cameraroot_yaw
        cameraroot["pitch"] = 0
        cameraroot["roll"] = 0
        keyframe["cameraroot"] = cameraroot

        camera_local_x = extrinsics[keyframe_index][0] + vcam_x_offset
        camera_local_y = extrinsics[keyframe_index][1]
        camera_local_z = extrinsics[keyframe_index][2] + vcam_height_offset
        camera_local_yaw = extrinsics[keyframe_index][3]
        camera_local_pitch = extrinsics[keyframe_index][4] + vcam_pitch_offset
        camera_local_roll = extrinsics[keyframe_index][5]

        keyframe["camera_local"] = { "x": camera_local_x, "y": camera_local_y, "z": camera_local_z, "yaw": camera_local_yaw, "pitch": camera_local_pitch, "roll": camera_local_roll }
        keyframe["type"] = "auto"

        keyframes.append(keyframe)

    return keyframes


def generate_camera_movement(csv_path, config_camera_movement, config_type):

    c_default = config_camera_movement

    sequences = read_csv(csv_path)
    output = {}
    output["info"] = {}
    output["info"]["fps"] = 30
    output["info"]["config_type"] = config_type
    output["info"]["config"] = config_camera_movement._asdict()

    dolly_types_current = []
    look_at_target_bodyparts_current = []

    body_yaw = {}
    if c_default.theta_front or c_default.vcam_theta_front:
        # Load body yaw reference
        with open(MOTION_STATS_PATH, 'r') as f:
            csv_reader = csv.DictReader(f)
            for row in csv_reader:
                body_id = row["body_id"]
                motion_id = row["motion_id"]
                body = f"{body_id}_{motion_id}"
                yaw =row["pelvis_world_yaw_deg"]
                body_yaw[body] = float(yaw)

    vcam_captures = {}
    if c_default.vcam:
        # Load VCam captures information
        with open(VCAM_CAPTURES, "r") as f:
            vcam_captures = json.load(f)

    for sequence_name, sequence in sequences.items():
        c = c_default._replace() # make shallow copy since we might modify its values later for this sequence
        output_sequence = {}
        info = {}
        #camera_world_height = sequence["camera"]["z"]
        info["cameraroot_yaw_reference"] = sequence["cameraroot"]["yaw"]
        info["ground_height_world"] = sequence["ground_height_world"]

        # HFOV
        hfov_range_index = None
        if len(c.hfov_ranges) == 0:
            hfov = sequence["hfov"] # use HFOV from sequence
        else:
            hfov_range_index = random.randint(0, len(c.hfov_ranges) - 1)

            (hfov_min, hfov_max) = c.hfov_ranges[hfov_range_index]
            hfov = random.uniform(hfov_min, hfov_max)

        # Use keyframed VCam if specified
        if c.vcam:
            vcam_focallength = c.vcam_focallength_ranges[hfov_range_index]
            info["vcam_focallength"] = vcam_focallength

            # Get random capture file
            vcam_capture = random.choice(vcam_captures[c.vcam_type[0]][c.vcam_type[1]][vcam_focallength])
            info["vcam_capture"] = vcam_capture

            keyframes = get_vcam_keyframes(c, sequence, hfov, body_yaw, vcam_focallength, vcam_capture, info)
            output_sequence["keyframes"] = keyframes
            output_sequence["info"] = info
            output[sequence_name] = output_sequence
            continue

        # Check for camera height range overrides
        camera_height_min = c.camera_height_min
        camera_height_max = c.camera_height_max

        if sequence["camera_height_min"] > 0:
            camera_height_min = max(sequence["camera_height_min"], camera_height_min)
            info["camera_height_min"] = camera_height_min

        if sequence["camera_height_max"] > 0:
            camera_height_max = min(sequence["camera_height_max"], camera_height_max)
            info["camera_height_max"] = camera_height_max

        if camera_height_min > 0:
            info["camera_height"] = random.uniform(camera_height_min, camera_height_max)
        else:
            info["camera_height"] = sequence["camera"]["z"]
        camera_world_height =  info["ground_height_world"] + info["camera_height"]
        info["camera_world_height"] = camera_world_height

        # Handle optional theta range overrides
        if "theta_min" in sequence:
            theta_min = sequence["theta_min"]
            theta_max = sequence["theta_max"]
            c = c._replace(theta_min = theta_min)
            c = c._replace(theta_max = theta_max)

        camera_autodistance_ref = 0.0
        if c.camera_autodistance:
            # Camera distance from given hfov
            h_ref = c.camera_autodistance_ref # HFOV 52 needs at least 400cm distance from origin to fully see body, h_ref = 400 * tan (52/2) = 200
            alpha = radians(hfov/2)
            camera_autodistance_ref = h_ref / tan(alpha)

        if c.follow:
            follow_camera_distance = c.follow_camera_distance
            if c.camera_autodistance:
                follow_camera_distance = camera_autodistance_ref + random.uniform(0.0, c.follow_camera_distance)
            else:
                follow_camera_distance = c.follow_camera_distance

            info["follow_camera_distance"] = follow_camera_distance
            info["follow_camera_yaw_offset"] = random.uniform(c.follow_camera_yaw_offset_min, c.follow_camera_yaw_offset_max)

        if len(c.camera_shake) > 0:
            variation = random.randint(0, 249)
            info["camera_shake"] = f"{c.camera_shake}_{variation:03d}"
            info["camera_shake_scale"] = c.camera_shake_intensity * random.uniform(0.75, 1.25)
            info["camera_shake_start_offset"] = random.randint(0, 100)

        if len(c.look_at_target_bodyparts) > 0:
            if len(look_at_target_bodyparts_current) == 0:
                look_at_target_bodyparts_current = list(c.look_at_target_bodyparts)
                random.shuffle(look_at_target_bodyparts_current)

            look_at_bodypart = look_at_target_bodyparts_current.pop(0)
            info["look_at_bodypart"] = look_at_bodypart

        if c.look_at or c.camera_local_autopitch:
            info["look_at_offset_z"] = c.look_at_offset_z + random.uniform(-c.look_at_offset_z_range, c.look_at_offset_z_range)

        if (c.camera_roll_min != 0.0) or (c.camera_roll_max != 0.0):
            info["camera_roll"] = random.uniform(c.camera_roll_min, c.camera_roll_max)

        if c.randomize_location:
            # Randomize cameraroot xy stage location
            cameraroot_x = sequence["cameraroot"]["x"] + random.uniform(-25.0, 25.0)
            cameraroot_y = sequence["cameraroot"]["y"] + random.uniform(-25.0, 25.0)

            camera_radius_max = sequence["camera_radius_max"]
            if (camera_radius_max > 0):
                if c.camera_autodistance:
                    camera_radius_max_offset = (camera_autodistance_ref + c.distance_max) - camera_radius_max
                    if camera_radius_max_offset > 0:
                        # We are overshooting maximum camera radius, reduce distance max by offset
                        delta_distance = c.distance_max - c.distance_min
                        c = c._replace(distance_max = (c.distance_max - camera_radius_max_offset))

                        # Adjust distance min to be smaller than new max
                        c = c._replace(distance_min = (c.distance_max - delta_distance))

                        info["distance_min"] = c.distance_min
                        info["distance_max"] = c.distance_max

                else:
                    # Update local camera distance randomization configuration values
                    # New values will be stored in the sequence "info" field
                    if c.distance_max > camera_radius_max:
                        c = c._replace(distance_max = camera_radius_max)
                        info["distance_max"] = c.distance_max

                        distance_min_threshold = 0.9 * camera_radius_max # Ensure at least 10% distance difference
                        if c.distance_min > distance_min_threshold:
                            c = c._replace(distance_min = distance_min_threshold)
                            info["distance_min"] = c.distance_min

                        delta_max = c.distance_max - c.distance_min
                        distance_delta_threshold = 0.25 * delta_max # set upper boundary for mindelta

                        if c.distance_mindelta > distance_delta_threshold:
                            c = c._replace(distance_mindelta = distance_delta_threshold)
                            info["distance_mindelta"] = c.distance_mindelta

                        if c.distance_maxdelta > delta_max:
                            c = c._replace(distance_maxdelta = delta_max)
                            info["distance_maxdelta"] = c.distance_maxdelta

        if len(c.dolly_types) > 0:
            if len(dolly_types_current) == 0:
                dolly_types_current = list(c.dolly_types)
                random.shuffle(dolly_types_current)

            dolly_type = dolly_types_current.pop(0)
            distance = 0
            if dolly_type == "x":
                # Use fixed local Y offset
                c = c._replace(camera_local_y_min = 0.0)
                c = c._replace(camera_local_y_max = 0.0)
                c = c._replace(camera_local_y_mindelta = 0.0)
                c = c._replace(camera_local_y_maxdelta = 0.0)
            elif dolly_type == "y":
                # Use fixed X offset
                distance = random.uniform(c.distance_min, c.distance_max)
                c = c._replace(distance_min = distance)
                c = c._replace(distance_max = distance)
                c = c._replace(distance_mindelta = 0.0)
                c = c._replace(distance_maxdelta = 0.0)

            if "y" in dolly_type:
                if c.camera_autodistance:
                    # Override local Y range
                    x = camera_autodistance_ref + distance
                    y_max = x * tan(radians(hfov/2))
                    camera_local_y_offset_max = y_max - c.camera_local_y_stage
                    if camera_local_y_offset_max <= 0:
                        print(f"ERROR: Invalid autodistance local y max offset: {camera_local_y_offset_max}")
                        sys.exit(1)

                    c = c._replace(camera_local_y_min = -camera_local_y_offset_max)
                    c = c._replace(camera_local_y_max = camera_local_y_offset_max)
                    c = c._replace(camera_local_y_mindelta = 0.0)
                    c = c._replace(camera_local_y_maxdelta = 2 * camera_local_y_offset_max)
                    c = c._replace(camera_local_y_mindelta = 0.75 * camera_local_y_offset_max)

        distance = 0.0
        theta = 0.0
        phi = 0.0
        camera_local_y = 0.0
        camera_local_z = 0.0
        camera_local_pitch = None

        keyframes = []
        for keyframe_index in range(c.keyframes):
            keyframe = {}
            if keyframe_index == 0:
                keyframe["frame_index"] = -1 # set at -1 for proper motion blur at frame 0
                if c.randomize_location:
                    (distance, theta, phi, camera_local_y, camera_local_z) = get_random_location(c)

                    if c.camera_local_autopitch:
                        camera_local_pitch = -degrees(atan( (info["camera_height"] - info["look_at_offset_z"]) / abs(camera_autodistance_ref + distance)))
            elif keyframe_index == (c.keyframes - 1):
                keyframe["frame_index"] = sequence["frames"]

                if c.hfov_mindelta >= 0:
                    # Zoom in/out
                    hfov = get_random_hfov(c, hfov)

                if c.randomize_location:
                    (distance, theta, phi, camera_local_y, camera_local_z) = get_random_location(c, distance, theta, phi, camera_local_y, camera_local_z)
            else:
                print("ERROR: Currently only 2 keyframes supported", file=sys.stderr)
                sys.exit(1)

            keyframe["hfov"] = hfov

            if c.randomize_location:
                # Place cameraroot at desired height above ground
                cameraroot = {}
                cameraroot["x"] = cameraroot_x
                cameraroot["y"] = cameraroot_y
                cameraroot["z"] = camera_world_height

                if not c.theta_front:
                    cameraroot["yaw"] = sequence["cameraroot"]["yaw"] + theta
                else:
                    # Use theta as relative offset to first body front
                    sequence_body = sequence["body"]
                    sequence_body_yaw = sequence["body_yaw"]
                    body_yaw_offset = -body_yaw[sequence_body] # convert right-hand rule yaw to Unreal left-hand rule yaw

                    # Unreal default body is facing positive Y axis, camera is along negative X axis
                    # -90 yaw rotates cameraroot so that camera is looking along negative Y axis
                    cameraroot_yaw = -90.0 + sequence_body_yaw + body_yaw_offset
                    cameraroot["yaw"] = cameraroot_yaw + theta
                    info["theta"] = theta

                cameraroot["pitch"] = phi
                keyframe["cameraroot"] = cameraroot

                camera_local_x = -(camera_autodistance_ref + distance) # if camera_autodistance is used then distance denotes offset relative to autodistance point
                keyframe["camera_local"] = { "x": camera_local_x, "y": camera_local_y, "z": camera_local_z } # distance is along negative X
                if c.camera_local_autopitch:
                    keyframe["camera_local"]["pitch"] = camera_local_pitch

            keyframe["type"] = "linear"

            keyframes.append(keyframe)

        output_sequence["keyframes"] = keyframes
        output_sequence["info"] = info
        output[sequence_name] = output_sequence

    print(json.dumps(output, indent=4))

    json_output_path = csv_path.parent / "be_camera_animations.json"
    print(f"Saving camera animations: {json_output_path}")
    with open(json_output_path, "w") as f:
        json.dump(output, f, indent=4)

    return

def print_usage():
    print(f"Usage: {sys.argv[0]} INPUTCSVPATH CONFIGTYPE", file=sys.stderr)
    print("       %s be_seq.csv cam_default" % (sys.argv[0]), file=sys.stderr)
    print(configs_camera_movement.keys())
    return

################################################################################
# Main
################################################################################

if len(sys.argv) != 3:
    print_usage()
    sys.exit(1)

csv_path = Path(sys.argv[1])
config_type = sys.argv[2]

if not config_type in configs_camera_movement:
    print(f"ERROR: Undefined camera movement type: {config_type}", file=sys.stderr)
    print(configs_camera_movement.keys())
    sys.exit(1)

generate_camera_movement(csv_path, configs_camera_movement[config_type], config_type)

sys.exit(0)
