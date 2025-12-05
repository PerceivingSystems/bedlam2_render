# Copyright (c) 2025 Max Planck Society
# License: https://bedlam2.is.tuebingen.mpg.de/license.html
#
# Export selected captured Virtual Camera LevelSequence intrinsics and keyframed extrinsics to .json
#
# Usage:
# + Select desired "VCamActor_" sequences under /Game/Cinematics/Takes/ before executing script
#
# Requirements:
# + Enable Python plugin
#

import json
from pathlib import Path
import sys

import unreal

TARGET_ROOT=r"C:\bedlam\animations\vcam"
TARGET_FPS=30
LS_PREFIX="VCamActor_Record_"

def export_vcam(level_sequence, target_root, target_fps):
    vcam_spawnable = level_sequence.get_spawnables()[0] # VamActor_Record spawnable CineCamera

    # Get VCamActor_Record (CineCameraActor) initial world offset
    vcam_actor_transform_channels = None
    tracks = vcam_spawnable.get_tracks()
    for track in tracks:
        if isinstance(track, unreal.MovieScene3DTransformTrack):
            vcam_actor_transform_channels = track.get_sections()[0].get_all_channels()

    actor_x = vcam_actor_transform_channels[0].get_default()
    actor_y = vcam_actor_transform_channels[1].get_default()
    actor_z = vcam_actor_transform_channels[2].get_default()
    actor_roll = vcam_actor_transform_channels[3].get_default()
    actor_pitch = vcam_actor_transform_channels[4].get_default()
    actor_yaw = vcam_actor_transform_channels[5].get_default()

    actor_location = unreal.Vector(actor_x, actor_y, actor_z)
    actor_rotation = unreal.Rotator(actor_roll, actor_pitch, actor_yaw)

    unreal.log(f"  [INFO] VCamActor_Record actor world pose: T[{actor_x}, {actor_y}, {actor_z}], R[roll={actor_roll}, pitch={actor_pitch}, yaw={actor_yaw}]")

    # Get CameraComponent local space keyframes
    camera_component_channels = None
    camera_component_binding = vcam_spawnable.get_child_possessables()[0]
    tracks = camera_component_binding.get_tracks()
    for track in tracks:
        if isinstance(track, unreal.MovieScene3DTransformTrack):
            start_frame = track.get_sections()[0].get_start_frame()
            end_frame = track.get_sections()[0].get_end_frame()
            num_frames = end_frame - start_frame + 1
            unreal.log(f"  [INFO] Frame range: [{start_frame}, {end_frame}], num_frames={num_frames}")
            camera_component_channels = track.get_sections()[0].get_all_channels()

    # Captures keyframes are reduced, we need to evaluate all channels so that we have keyframe for every frame (baked keys)
    frame_rate = unreal.FrameRate(numerator = target_fps, denominator = 1)
    channel =  camera_component_channels[0] # x
    scripting_range = channel.compute_effective_range()
    keyframes_evaluated_x = channel.evaluate_keys(scripting_range, frame_rate)

    channel =  camera_component_channels[1] # y
    scripting_range = channel.compute_effective_range()
    keyframes_evaluated_y = channel.evaluate_keys(scripting_range, frame_rate)

    channel =  camera_component_channels[2] # z
    scripting_range = channel.compute_effective_range()
    keyframes_evaluated_z = channel.evaluate_keys(scripting_range, frame_rate)

    channel =  camera_component_channels[3] # roll
    scripting_range = channel.compute_effective_range()
    keyframes_evaluated_roll = channel.evaluate_keys(scripting_range, frame_rate)

    channel =  camera_component_channels[4] # pitch
    scripting_range = channel.compute_effective_range()
    keyframes_evaluated_pitch = channel.evaluate_keys(scripting_range, frame_rate)

    channel =  camera_component_channels[5] # yaw
    scripting_range = channel.compute_effective_range()
    keyframes_evaluated_yaw = channel.evaluate_keys(scripting_range, frame_rate)

    unreal.log(f"  [INFO] Local camera component evaluated keyframes: x [{len(keyframes_evaluated_x)}], y [{len(keyframes_evaluated_y)}], z [{len(keyframes_evaluated_z)}], roll [{len(keyframes_evaluated_roll)}], pitch [{len(keyframes_evaluated_pitch)}], yaw [{len(keyframes_evaluated_yaw)}]")

    # Transform camera component location/rotation to world space
    actor_transform = unreal.Transform(actor_location, actor_rotation)
    num_frames = len(keyframes_evaluated_x)
    keyframes_world_location = []
    keyframes_world_rotation = []
    for i in range(num_frames):
        local_location = unreal.Vector(keyframes_evaluated_x[i], keyframes_evaluated_y[i], keyframes_evaluated_z[i])
        world_location = actor_transform.transform_location(local_location)
        keyframes_world_location.append(world_location)

        local_rotation = unreal.Rotator(keyframes_evaluated_roll[i], keyframes_evaluated_pitch[i], keyframes_evaluated_yaw[i])
        world_rotation = actor_transform.transform_rotation(local_rotation)
        keyframes_world_rotation.append(world_rotation)

    # Get CineCamera intrinsics
    cinecamera_object_template = vcam_spawnable.get_object_template()
    camera_component = cinecamera_object_template.camera_component
    focal_length  = camera_component.current_focal_length
    hfov          = camera_component.get_editor_property("current_horizontal_fov")
    sensor_width  = camera_component.filmback.sensor_width
    sensor_height = camera_component.filmback.sensor_height

    # Create export data dictionary
    # Rotations are stored in order of execution: yaw => pitch => roll
    sequence_path = level_sequence.get_path_name()
    data = { "info": { "num_frames" : num_frames, "fps" : target_fps, "source_sequence_path" : sequence_path, "keyframe_data" : "x_ue,y_ue,z_ue,yaw_ue,pitch_ue,roll_ue"} }

    data["intrinsics"] = {"focal_length": [focal_length], "hfov": [hfov], "sensor_width" : sensor_width, "sensor_height" : sensor_height }

    keyframes = []
    for i in range(num_frames):
        world_location = keyframes_world_location[i]
        world_rotation = keyframes_world_rotation[i]

        keyframe = [world_location.x, world_location.y, world_location.z, world_rotation.yaw, world_rotation.pitch, world_rotation.roll]
        keyframes.append(keyframe)

    data["extrinsics"] = keyframes

    # Save data in JSON format
    capture_day = sequence_path.split("/")[4] # /Game/Cinematics/Takes/2024-07-17/Scene_1_04_Subscenes/VCamActor_Record_Scene_1_04.VCamActor_Record_Scene_1_04
    capture_day = capture_day.replace("-", "")
    take = int(sequence_path.rsplit("_", maxsplit=1)[1])
    json_output_path = target_root / f"vcam_{capture_day}_{take:04d}.json"
    unreal.log(f"Saving camera animations: {json_output_path}")

    if not json_output_path.parent.exists():
        json_output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(json_output_path, "w") as f:
        json.dump(data, f, indent=4)

    return True

def get_keyframes_world(keyframes, offset):
    keyframes_world = [(x + offset) for x in keyframes]
    return keyframes_world

######################################################################
# Main
######################################################################
unreal.log(f"======================================================================")
unreal.log(f"Running {__file__}")
target_root = Path(TARGET_ROOT)
unreal.log(f"Export directory: {target_root}")

selection = unreal.EditorUtilityLibrary.get_selected_assets() # Loads all selected assets so very slow operation when selecting whole dataset

processed_sequences = False
for asset in selection:
    unreal.log(f"Processing: {asset.get_name()}")
    if not isinstance(asset, unreal.LevelSequence):
        unreal.log_error("ERROR: not a LevelSequence")
        sys.exit(1)

    if not asset.get_name().startswith(LS_PREFIX):
        unreal.log_error(f"ERROR: Wrong VCam LevelSequence. Only sequences with prefix '{LS_PREFIX}' can be exported")
        sys.exit(1)


    status = export_vcam(asset, target_root, TARGET_FPS)
    if not status:
        unreal.log_error("Failure")
        sys.exit(1)
    else:
        processed_sequences = True

if not processed_sequences:
    unreal.log_error("No selected LevelSequences")
    sys.exit(1)

unreal.log("Export finished. No errors detected.")
