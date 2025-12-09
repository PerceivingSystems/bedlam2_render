# Copyright (c) 2025 Max Planck Society
# License: https://bedlam2.is.tuebingen.mpg.de/license.html
#
# Create level sequences for specified animations in be_seq.csv file
#
# Required plugins: Python Editor Script Plugin, Editor Scripting, Sequencer Scripting, Groom
#

from configparser import NoOptionError
import csv
from dataclasses import dataclass
import json
from math import radians, tan
from pathlib import Path
import re
import sys
import time
import unreal

# Globals
WARMUP_FRAMES = 10 # Needed for proper temporal sampling on frame 0 of animations and raytracing warmup. These frames are rendered out with negative numbers and will be deleted in post render pipeline.
data_root_unreal = "/Engine/PS/Bedlam/"
camera_shake_root = data_root_unreal + "Core/Camera/ShakeVariations/"
clothing_actor_class_path = data_root_unreal + "Core/Materials/BE_ClothingOverlayActor.BE_ClothingOverlayActor_C"
body_root = data_root_unreal + "SMPLX_LH/"
clothing_root = data_root_unreal + "Clothing/"
hair_root = data_root_unreal + "Hair/VineFX/"
animation_root = data_root_unreal + "SMPLX_LH_animations/"

hdri_root = data_root_unreal + "HDRI/8k/"
hdri_suffix = "_8k"

material_body_root = "/Engine/PS/Meshcapade/SMPLX/Materials"
material_clothing_root = data_root_unreal + "Clothing/Materials"
texture_body_root = "/Engine/PS/Meshcapade/SMPLX/Textures"
texture_clothing_overlay_root = data_root_unreal + "Clothing/MaterialsSMPLX/Textures"

material_hidden_name = data_root_unreal + "Core/Materials/M_SMPLX_Hidden"

material_hair_root = data_root_unreal + "Core/Materials/Hair"

material_shoe_root = data_root_unreal + "Shoes/Materials"


bedlam_root = "/Game/Bedlam/"
level_sequence_hdri_prefix = bedlam_root + "LS_Template_"
level_sequences_root = bedlam_root + "LevelSequences/"
camera_root = bedlam_root + "CameraMovement/"
csv_path = r"C:\bedlam2\images\test\be_seq.csv"
camera_animation_filename = "be_camera_animations.json"

################################################################################

@dataclass
class SequenceBody:
    subject: str
    body_path: str
    clothing_path: str
    hair_path: str
    animation_path: str
    x: float
    y: float
    z: float
    yaw: float
    pitch: float
    roll: float
    start_frame: int
    texture_body: str
    texture_clothing: str
    texture_clothing_overlay: str
    haircolor_path: str
    shoe: str

@dataclass
class ActorPose:
    x: float
    y: float
    z: float
    yaw: float
    pitch: float
    roll: float

################################################################################

def add_geometry_cache(level_sequence, sequence_body_index, layer_suffix, start_frame, end_frame, target_object, groom_asset, groom_binding, groom_material, x, y, z, yaw, pitch, roll, material=None, texture_body_path=None, texture_clothing_overlay_path=None):
    """
    Add geometry cache to LevelSequence and setup material.
    If material parameter is set then GeometryCacheActor will be spawned and the material will be used.
    Otherwise a custom clothing actor (SMPLXClothingActor) will be spawned and the provided texture inputs will be used.
    """

    # Spawned GeometryCaches will generate GeometryCacheActors where ManualTick is false by default.
    # This will cause the animation to play before the animation section in the timeline and lead to temporal sampling errors
    # on the first frame of the animation section.
    # To prevent this we need to set ManualTick to true as default setting for the GeometryCacheActor.
    # 1. Spawn default GeometryCacheActor template in level
    # 2. Set default settings for GeometryCache and ManualTick on it
    # 3. Add actor as spawnable to sequence
    # 4. Destroy template actor in level
    # Note: Conversion from possessable to spawnable currently not available in Python: https://forums.unrealengine.com/t/convert-to-spawnable-with-python/509827

    if texture_clothing_overlay_path is not None:
        # Use SMPL-X clothing overlay texture, dynamic material instance will be generated in BE_ClothingOverlayActor Construction Script
        clothing_actor_class = unreal.load_class(None, clothing_actor_class_path)
        geometry_cache_actor = unreal.get_editor_subsystem(unreal.EditorActorSubsystem).spawn_actor_from_class(clothing_actor_class, unreal.Vector(0,0,0))
        geometry_cache_actor.set_editor_property("bodytexture", unreal.SystemLibrary.conv_soft_obj_path_to_soft_obj_ref(unreal.SoftObjectPath(texture_body_path)))
        geometry_cache_actor.set_editor_property("clothingtextureoverlay", unreal.SystemLibrary.conv_soft_obj_path_to_soft_obj_ref(unreal.SoftObjectPath(texture_clothing_overlay_path)))
    else:
        geometry_cache_actor = unreal.get_editor_subsystem(unreal.EditorActorSubsystem).spawn_actor_from_class(unreal.GeometryCacheActor, unreal.Vector(0,0,0))
        if material is not None:
            geometry_cache_actor.get_geometry_cache_component().set_material(0, material)


    geometry_cache_actor.set_actor_label(target_object.get_name())
    geometry_cache_actor.get_geometry_cache_component().set_editor_property("looping", False) # disable looping to prevent ghosting on last frame with temporal sampling
    geometry_cache_actor.get_geometry_cache_component().set_editor_property("manual_tick", True)
    geometry_cache_actor.get_geometry_cache_component().set_editor_property("geometry_cache", target_object)

    # Add hair
    if groom_asset is not None:
        unreal.log(f"    Adding hair: {hair_path}")

        # Attach Groom component to GeometryCacheActor
        sod = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
        root_object = sod.k2_gather_subobject_data_for_instance(geometry_cache_actor)[0]
        subobject_handle, fail_reason = sod.add_new_subobject(unreal.AddNewSubobjectParams(parent_handle=root_object, new_class=unreal.GroomComponent))
        if not fail_reason.is_empty():
            unreal.log_error("ERROR: Cannot add Groom component via SubobjectDataSubsystem: {fail_reason}")
            return

        # Set groom and binding for the new groom component
        sodbpfl = unreal.SubobjectDataBlueprintFunctionLibrary
        groom_component = sodbpfl.get_object(sodbpfl.get_data(subobject_handle))
        groom_component.set_groom_asset(groom_asset)
        groom_component.set_binding_asset(groom_binding)

        groom_component.set_material(0, groom_material)

    # Add actor to new layer so that we can later use layer name when generating segmentation masks names.
    # Note: We cannot use ObjectIds of type "Actor" since actors which are added via add_spawnable_from_instance() will later use their class names when generating ObjectIds of type Actor.
    layer_subsystem = unreal.get_editor_subsystem(unreal.LayersSubsystem)
    layer_name = f"be_actor_{sequence_body_index:02}_{layer_suffix}"
    result = layer_subsystem.add_actor_to_layer(geometry_cache_actor, layer_name)
    if not result:
        # If World Partition system is used for the current map (CitySample), the layer system is not available and adding actors to layers will fail.
        # Use folder names in this case.
        unreal.log_warning("WARNING: Layer system not available due to World Partition map, using folder names to identify body/clothing mask layers")
        geometry_cache_actor.set_folder_path(f"BEDLAM/masks/{layer_name}")

    body_binding = level_sequence.add_spawnable_from_instance(geometry_cache_actor)
    unreal.get_editor_subsystem(unreal.EditorActorSubsystem).destroy_actor(geometry_cache_actor) # Delete temporary template actor from level

    geometry_cache_track = body_binding.add_track(unreal.MovieSceneGeometryCacheTrack)
    geometry_cache_section = geometry_cache_track.add_section()
    geometry_cache_section.set_range(start_frame, end_frame)

    # TODO properly set Geometry Cache target in geometry_cache_section properties to have same behavior as manual setup
    #
    # Not working: geometry_cache_section.set_editor_property("GeometryCache", body_object)
    #   Exception: MovieSceneGeometryCacheTrack: Failed to find property 'GeometryCache' for attribute 'GeometryCache' on 'MovieSceneGeometryCacheTrack'

    transform_track = body_binding.add_track(unreal.MovieScene3DTransformTrack)
    transform_section = transform_track.add_section()
    transform_section.set_start_frame_bounded(False)
    transform_section.set_end_frame_bounded(False)
    transform_channels = transform_section.get_all_channels()
    transform_channels[0].set_default(x) # location X
    transform_channels[1].set_default(y) # location Y
    transform_channels[2].set_default(z) # location Z

    transform_channels[3].set_default(roll)  # roll
    transform_channels[4].set_default(pitch) # pitch
    transform_channels[5].set_default(yaw)   # yaw

    return

def add_animation(level_sequence, start_frame, end_frame, animation_path, x, y, z, yaw, pitch, roll,):
    """
    Add animation sequence to LevelSequence.
    """

    unreal.log(f"    Loading animation sequence: {animation_path}")
    animsequence_object = unreal.load_asset(animation_path)
    if animsequence_object is None:
        unreal.log_error("      Cannot load animation sequence")
        return False


    # SkeletalMesh'/Engine/PS/Bedlam/SMPLX_batch01_hand_animations/rp_aaron_posed_002/rp_aaron_posed_002_1038.rp_aaron_posed_002_1038'
    animation_path_name = animation_path.split("/")[-1]
    animation_path_root = animation_path.replace(animation_path_name, "")
    skeletal_mesh_path = animation_path_root + animation_path_name.replace("_Anim", "")
    unreal.log(f"    Loading skeletal mesh: {skeletal_mesh_path}")
    skeletal_mesh_object = unreal.load_asset(skeletal_mesh_path)
    if skeletal_mesh_object is None:
        unreal.log_error("      Cannot load skeletal mesh")
        return False

    skeletal_mesh_actor = unreal.get_editor_subsystem(unreal.EditorActorSubsystem).spawn_actor_from_class(unreal.SkeletalMeshActor, unreal.Vector(0,0,0))
    skeletal_mesh_actor.set_actor_label(animsequence_object.get_name())
    skeletal_mesh_actor.skeletal_mesh_component.set_skeletal_mesh(skeletal_mesh_object)

    # Set hidden material to hide the skeletal mesh
    material = unreal.EditorAssetLibrary.load_asset(f"Material'{material_hidden_name}'")
    if not material:
        unreal.log_error("Cannot load hidden material: " + material_hidden_name)
    skeletal_mesh_actor.skeletal_mesh_component.set_material(0, material)

    # Setup LevelSequence
    skeletal_mesh_actor_binding = level_sequence.add_spawnable_from_instance(skeletal_mesh_actor)

    unreal.get_editor_subsystem(unreal.EditorActorSubsystem).destroy_actor(skeletal_mesh_actor) # Delete temporary template actor from level

    anim_track = skeletal_mesh_actor_binding.add_track(unreal.MovieSceneSkeletalAnimationTrack)
    anim_section = anim_track.add_section()
    anim_section.params.animation = animsequence_object
    anim_section.set_range(start_frame, end_frame)

    transform_track = skeletal_mesh_actor_binding.add_track(unreal.MovieScene3DTransformTrack)
    transform_section = transform_track.add_section()
    transform_section.set_start_frame_bounded(False)
    transform_section.set_end_frame_bounded(False)
    transform_channels = transform_section.get_all_channels()
    transform_channels[0].set_default(x) # location X
    transform_channels[1].set_default(y) # location Y
    transform_channels[2].set_default(z) # location Z
    transform_channels[3].set_default(roll)  # roll
    transform_channels[4].set_default(pitch) # pitch
    transform_channels[5].set_default(yaw)   # yaw

    return skeletal_mesh_actor_binding

def attach_camera_target(level_sequence, skeletal_mesh_actor_binding, attach_socket_name, camera_target_actor, camera_target_actor_location=None):

    target_binding = level_sequence.add_possessable(camera_target_actor)
    if skeletal_mesh_actor_binding is not None:
        attach_track = target_binding.add_track(unreal.MovieScene3DAttachTrack)
        attach_section = attach_track.add_section() # MovieScene3DAttachSection
        attach_section.set_start_frame_bounded(False)
        attach_section.set_end_frame_bounded(False)

        animation_binding_id = unreal.MovieSceneObjectBindingID()
        animation_binding_id.set_editor_property("Guid", skeletal_mesh_actor_binding.get_id())
        attach_section.set_constraint_binding_id(animation_binding_id)
        attach_section.set_editor_property("attach_socket_name", attach_socket_name)

        add_transform_track(target_binding, ActorPose(0, 0, 0, 0, 0, 0))
    else:
        # Put camera target at fixed world space location
        add_transform_track(target_binding, ActorPose(camera_target_actor_location.x, camera_target_actor_location.y, camera_target_actor_location.z, 0, 0, 0))
    return True

def add_transform_track(binding, actor_pose):
    transform_track = binding.add_track(unreal.MovieScene3DTransformTrack)
    transform_section = transform_track.add_section()
    transform_section.set_start_frame_bounded(False)
    transform_section.set_end_frame_bounded(False)
    transform_channels = transform_section.get_all_channels()
    transform_channels[0].set_default(actor_pose.x) # location X
    transform_channels[1].set_default(actor_pose.y) # location Y
    transform_channels[2].set_default(actor_pose.z) # location Z

    transform_channels[3].set_default(actor_pose.roll) # roll
    transform_channels[4].set_default(actor_pose.pitch) # pitch
    transform_channels[5].set_default(actor_pose.yaw) # yaw
    return

def get_focal_length(cine_camera_component, camera_hfov):
    sensor_width = cine_camera_component.filmback.sensor_width
    focal_length = sensor_width / (2.0 * tan(radians(camera_hfov)/2))
    return focal_length

def add_static_camera(level_sequence, camera_actor, camera_pose, camera_hfov):
    """
    Add static camera actor and camera cut track to level sequence.
    """

    # Add camera with transform track
    camera_binding = level_sequence.add_possessable(camera_actor)
    if camera_pose is not None:
        add_transform_track(camera_binding, camera_pose)

    # Add focal length CameraComponent track to match specified hfov

    # Add a cine camera component binding using the component of the camera actor
    cine_camera_component = camera_actor.get_cine_camera_component()
    camera_component_binding = level_sequence.add_possessable(cine_camera_component)
    camera_component_binding.set_parent(camera_binding)

    focal_length_track = camera_component_binding.add_track(unreal.MovieSceneFloatTrack)
    focal_length_track.set_property_name_and_path('CurrentFocalLength', 'CurrentFocalLength')
    focal_length_section = focal_length_track.add_section()
    focal_length_section.set_start_frame_bounded(False)
    focal_length_section.set_end_frame_bounded(False)

    if camera_hfov is not None:
        focal_length = get_focal_length(cine_camera_component, camera_hfov)
        focal_length_section.get_all_channels()[0].set_default(focal_length)

    camera_cut_track = level_sequence.add_master_track(unreal.MovieSceneCameraCutTrack)
    camera_cut_section = camera_cut_track.add_section()
    camera_cut_section.set_start_frame(-WARMUP_FRAMES) # Use negative frames as warmup frames
    camera_binding_id = unreal.MovieSceneObjectBindingID()
    camera_binding_id.set_editor_property("Guid", camera_binding.get_id())
    camera_cut_section.set_editor_property("CameraBindingID", camera_binding_id)

    return (camera_binding, camera_component_binding, camera_cut_section)

def change_binding_end_keyframe_times(binding, new_frame):
    for track in binding.get_tracks():
        for section in track.get_sections():
            for channel in section.get_all_channels():
                channel_keys = channel.get_keys()
                if len(channel_keys) > 0:
                    if len(channel_keys) != 2: # only change end keyframe time if channel has two keyframes
                        unreal.log_error("WARNING: Channel does not have two keyframes. Not changing last keyframe to sequence end frame.")
                    else:
                        end_key = channel_keys[1]
                        end_key.set_time(unreal.FrameNumber(new_frame))

def add_camera_animation(camera_animations, level_sequence, sequence_name, cameraroot_binding, camera_binding, sequence_frames):
    print(f"  Adding camera animation: {sequence_name}")

    if cameraroot_binding is not None:
        # Add camera root actor track defaults
        cameraroot = camera_animations[sequence_name]["keyframes"][0]["cameraroot"]
        cameraroot_transform_track = cameraroot_binding.add_track(unreal.MovieScene3DTransformTrack)
        cameraroot_transform_section = cameraroot_transform_track.add_section()
        cameraroot_transform_section.set_start_frame_bounded(False)
        cameraroot_transform_section.set_end_frame_bounded(False)
        cameraroot_transform_channels = cameraroot_transform_section.get_all_channels()
        cameraroot_transform_channels[0].set_default(cameraroot["x"])
        cameraroot_transform_channels[1].set_default(cameraroot["y"])
        cameraroot_transform_channels[2].set_default(cameraroot["z"])
        cameraroot_transform_channels[3].set_default(0.0) # roll
        cameraroot_transform_channels[4].set_default(cameraroot["pitch"])
        cameraroot_transform_channels[5].set_default(cameraroot["yaw"])

    # Add keyframes
    camera_transform_track = camera_binding.get_tracks()[0]
    camera_transform_section = camera_transform_track.get_sections()[0]
    camera_transform_channels = camera_transform_section.get_all_channels()

    for keyframe in camera_animations[sequence_name]["keyframes"]:

        # Set interpolation type
        interpolation = None
        type = keyframe["type"]
        if type == "auto":
            interpolation = unreal.MovieSceneKeyInterpolation.AUTO
        elif type == "linear":
            interpolation = unreal.MovieSceneKeyInterpolation.LINEAR
        else:
            unreal.log_error(f"Unsupported interpolation type {type}")
            return False

        frame_index = keyframe["frame_index"]
        if cameraroot_binding is not None:
            cameraroot = keyframe["cameraroot"]
            cameraroot_transform_channels[0].add_key(time=unreal.FrameNumber(frame_index), new_value=cameraroot["x"], interpolation=interpolation)
            cameraroot_transform_channels[1].add_key(time=unreal.FrameNumber(frame_index), new_value=cameraroot["y"], interpolation=interpolation)
            cameraroot_transform_channels[2].add_key(time=unreal.FrameNumber(frame_index), new_value=cameraroot["z"], interpolation=interpolation)
            cameraroot_transform_channels[4].add_key(time=unreal.FrameNumber(frame_index), new_value=cameraroot["pitch"], interpolation=interpolation)
            cameraroot_transform_channels[5].add_key(time=unreal.FrameNumber(frame_index), new_value=cameraroot["yaw"], interpolation=interpolation)

        if "camera_local" in keyframe:
            camera = keyframe["camera_local"]
            camera_transform_channels[0].add_key(time=unreal.FrameNumber(frame_index), new_value=camera["x"], interpolation=interpolation)
            camera_transform_channels[1].add_key(time=unreal.FrameNumber(frame_index), new_value=camera["y"], interpolation=interpolation)
            camera_transform_channels[2].add_key(time=unreal.FrameNumber(frame_index), new_value=camera["z"], interpolation=interpolation)

            if "roll" in camera:
                camera_transform_channels[3].add_key(time=unreal.FrameNumber(frame_index), new_value=camera["roll"], interpolation=interpolation)
            if "pitch" in camera:
                camera_transform_channels[4].add_key(time=unreal.FrameNumber(frame_index), new_value=camera["pitch"], interpolation=interpolation)
            if "yaw" in camera:
                camera_transform_channels[5].add_key(time=unreal.FrameNumber(frame_index), new_value=camera["yaw"], interpolation=interpolation)

    return True

def add_camera_hfov_animation(camera_animations, sequence_name, camera_component_binding, camera_actor):
    print(f"  Adding camera hfov animation: {sequence_name}")

    # Add keyframes

    focal_length_track = camera_component_binding.get_tracks()[0]
    if focal_length_track.get_display_name() != "CurrentFocalLength":
        unreal.log_error("  ERROR: Cannot find CurrentFocalLength track")

    focal_length_section = focal_length_track.get_sections()[0]
    focal_length_channels = focal_length_section.get_all_channels()

    cine_camera_component = camera_actor.get_cine_camera_component()

    for keyframe in camera_animations[sequence_name]["keyframes"]:

        # Set interpolation type
        interpolation = None
        type = keyframe["type"]
        if type == "auto":
            interpolation = unreal.MovieSceneKeyInterpolation.AUTO
        elif type == "linear":
            interpolation = unreal.MovieSceneKeyInterpolation.LINEAR
        else:
            unreal.log_error(f"Unsupported interpolation type {type}")
            return False

        frame_index = keyframe["frame_index"]

        if "hfov" in keyframe:
            hfov = keyframe["hfov"]
            focal_length = get_focal_length(cine_camera_component, hfov)
            focal_length_channels[0].add_key(time=unreal.FrameNumber(frame_index), new_value=focal_length, interpolation=interpolation)

    return True

def setup_lookat_camera(camera_animations, sequence_name, camera_binding):

    sequence_camera_data = camera_animations[sequence_name]

    if "camera_roll" in sequence_camera_data["info"]:
        camera_roll = sequence_camera_data["info"]["camera_roll"]
        camera_transform_track = camera_binding.get_tracks()[0]
        camera_transform_section = camera_transform_track.get_sections()[0]
        camera_transform_channels = camera_transform_section.get_all_channels()
        camera_transform_channels[3].set_default(camera_roll)

    lookat_track = camera_binding.add_track(unreal.MovieSceneBoolTrack)
    lookat_track.set_property_name_and_path("Enable Look at Tracking", "LookatTrackingSettings.bEnableLookAtTracking")
    lookat_track_section = lookat_track.add_section()
    lookat_track_section.set_start_frame_bounded(False)
    lookat_track_section.set_end_frame_bounded(False)
    lookat_track_channel = lookat_track_section.get_all_channels()[0]
    lookat_track_channel.set_default(True)

    if "look_at_interp_speed" in camera_animations["info"]["config"]:
        speed = camera_animations["info"]["config"]["look_at_interp_speed"]

        track = camera_binding.add_track(unreal.MovieSceneFloatTrack)
        track.set_property_name_and_path("LookAtTrackingInterpSpeed", "LookatTrackingSettings.LookAtTrackingInterpSpeed")
        track_section = track.add_section()
        track_section.set_start_frame_bounded(False)
        track_section.set_end_frame_bounded(False)
        track_channel = track_section.get_all_channels()[0]
        track_channel.set_default(speed)

    lookat_offset_track = camera_binding.add_track(unreal.MovieSceneDoubleVectorTrack)
    lookat_offset_track.set_property_name_and_path("Relative Offset", "LookatTrackingSettings.RelativeOffset")
    lookat_offset_track.set_num_channels_used(3) # note: will trigger assertion if not set
    lookat_offset_track_section = lookat_offset_track.add_section()
    lookat_offset_track_section.set_start_frame_bounded(False)
    lookat_offset_track_section.set_end_frame_bounded(False)

    offset_z = sequence_camera_data["info"]["look_at_offset_z"]

    lookat_offset_track_section.get_all_channels()[0].set_default(0.0)
    lookat_offset_track_section.get_all_channels()[1].set_default(0.0)
    lookat_offset_track_section.get_all_channels()[2].set_default(offset_z)

    return True

def setup_follow_camera(level_sequence, camera_binding, camera_operator_actor, camera_animations, sequence_name):

    sequence_camera_data = camera_animations[sequence_name]

    # Add camera operator and enable it
    camera_operator_binding = level_sequence.add_possessable(camera_operator_actor)
    enabled_track = camera_operator_binding.add_track(unreal.MovieSceneBoolTrack)
    enabled_track.set_property_name_and_path("EnableFollowCamera", "EnableFollowCamera")
    enabled_track_section = enabled_track.add_section()
    enabled_track_section.set_start_frame_bounded(False)
    enabled_track_section.set_end_frame_bounded(False)
    enabled_track_channel = enabled_track_section.get_all_channels()[0]
    enabled_track_channel.set_default(True)

    follow_static_location = camera_animations["info"]["config"]["follow_static_location"]
    if follow_static_location:
        enabled_track = camera_operator_binding.add_track(unreal.MovieSceneBoolTrack)
        enabled_track.set_property_name_and_path("StaticLocation", "StaticLocation")
        enabled_track_section = enabled_track.add_section()
        enabled_track_section.set_start_frame_bounded(False)
        enabled_track_section.set_end_frame_bounded(False)
        enabled_track_channel = enabled_track_section.get_all_channels()[0]
        enabled_track_channel.set_default(True)

    track = camera_operator_binding.add_track(unreal.MovieSceneFloatTrack)
    track.set_property_name_and_path("CameraHeight", "CameraHeight")
    track_section = track.add_section()
    track_section.set_start_frame_bounded(False)
    track_section.set_end_frame_bounded(False)
    track_channel = track_section.get_all_channels()[0]
    track_channel.set_default(sequence_camera_data["info"]["camera_height"])

    track = camera_operator_binding.add_track(unreal.MovieSceneFloatTrack)
    track.set_property_name_and_path("GroundHeightWorld", "GroundHeightWorld")
    track_section = track.add_section()
    track_section.set_start_frame_bounded(False)
    track_section.set_end_frame_bounded(False)
    track_channel = track_section.get_all_channels()[0]
    track_channel.set_default(sequence_camera_data["info"]["ground_height_world"])

    track = camera_operator_binding.add_track(unreal.MovieSceneFloatTrack)
    track.set_property_name_and_path("FollowCameraDistance", "FollowCameraDistance")
    track_section = track.add_section()
    track_section.set_start_frame_bounded(False)
    track_section.set_end_frame_bounded(False)
    track_channel = track_section.get_all_channels()[0]
    track_channel.set_default(sequence_camera_data["info"]["follow_camera_distance"])

    track = camera_operator_binding.add_track(unreal.MovieSceneFloatTrack)
    track.set_property_name_and_path("FollowCameraYawOffset", "FollowCameraYawOffset")
    track_section = track.add_section()
    track_section.set_start_frame_bounded(False)
    track_section.set_end_frame_bounded(False)
    track_channel = track_section.get_all_channels()[0]
    track_channel.set_default(sequence_camera_data["info"]["follow_camera_yaw_offset"])

    if "camera_roll" in sequence_camera_data["info"]:
        camera_roll = sequence_camera_data["info"]["camera_roll"]
        track = camera_operator_binding.add_track(unreal.MovieSceneFloatTrack)
        track.set_property_name_and_path("CameraRoll", "CameraRoll")
        track_section = track.add_section()
        track_section.set_start_frame_bounded(False)
        track_section.set_end_frame_bounded(False)
        track_channel = track_section.get_all_channels()[0]
        track_channel.set_default(camera_roll)

    # Note: follow camera has no transform track so we do not need to zero out unwanted offset values

    return True

def setup_camera_sensor(camera_component_binding, sensor_width, sensor_height):
    sensor_width_track = camera_component_binding.add_track(unreal.MovieSceneFloatTrack)
    sensor_width_track.set_property_name_and_path('SensorWidth', 'Filmback.SensorWidth')
    sensor_width_section = sensor_width_track.add_section()
    sensor_width_section.set_start_frame_bounded(False)
    sensor_width_section.set_end_frame_bounded(False)
    sensor_width_section.get_all_channels()[0].set_default(sensor_width)

    sensor_height_track = camera_component_binding.add_track(unreal.MovieSceneFloatTrack)
    sensor_height_track.set_property_name_and_path('SensorHeight', 'Filmback.SensorHeight')
    sensor_height_section = sensor_height_track.add_section()
    sensor_height_section.set_start_frame_bounded(False)
    sensor_height_section.set_end_frame_bounded(False)
    sensor_height_section.get_all_channels()[0].set_default(sensor_height)

    return True

def setup_camera_shake(camera_component_binding, camera_shake_name, camera_shake_scale, sequence_frames, start_offset):
    camera_shake_track = camera_component_binding.add_track(unreal.MovieSceneCameraShakeTrack)
    camera_shake_section = camera_shake_track.add_section()
    # Note: We cannot use set_start_frame_bounded(False)/set_start_frame_bounded(False)
    #       since it will crash editor when generated sequence is opened in Sequencer (5.3.2)
    camera_shake_section.set_start_frame(-WARMUP_FRAMES-start_offset)
    camera_shake_section.set_end_frame(sequence_frames)

    shake_data = camera_shake_section.get_editor_property("shake_data")
    shake_data.set_editor_property("play_scale", camera_shake_scale)
    shake_class_name = camera_shake_name.rsplit("_", maxsplit=1)[0]
    shake_class_path = f"{camera_shake_root}{shake_class_name}/{camera_shake_name}.{camera_shake_name}_C"
    shake_class = unreal.load_class(None, shake_class_path)
    if shake_class is None:
        unreal.log_error(f"ERROR: Cannot load shake class: {shake_class_path}")
        return False
    shake_data.set_editor_property("shake_class", shake_class)

    return True

def setup_time_of_day(level_sequence, time_of_day, sunsky_actor):

    # Add SunSky actor
    sunsky_binding = level_sequence.add_possessable(sunsky_actor)
    track = sunsky_binding.add_track(unreal.MovieSceneFloatTrack)
    track.set_property_name_and_path("SolarTime", "SolarTime")
    track_section = track.add_section()
    track_section.set_start_frame_bounded(False)
    track_section.set_end_frame_bounded(False)
    track_channel = track_section.get_all_channels()[0]
    track_channel.set_default(time_of_day)

    return


def add_level_sequence(name, camera_actor, camera_pose, ground_truth_logger_actor, camera_target_actor, camera_operator_actor, sequence_bodies, sequence_frames, hdri_name, camera_hfov=None, camera_movement_type="Default", camera_animations=None, cameraroot_yaw=None, cameraroot_location=None, time_of_day=None, sunsky_actor=None):
    asset_tools = unreal.AssetToolsHelpers.get_asset_tools()

    level_sequences_root_current = level_sequences_root

    # Check if we use camera animations
    if camera_animations is not None:
        sequence_name = name
        camera_hfov = camera_animations[name]["keyframes"][0]["hfov"]
        if "camera_local" in camera_animations[name]["keyframes"][0]:
            pose = camera_animations[name]["keyframes"][0]["camera_local"]
            # Use first keyframe camera pose as default
            camera_pose = ActorPose(pose["x"], pose["y"], pose["z"], 0.0, 0.0, 0.0) # x,y,z,yaw,pitch,roll

    level_sequence_path = level_sequences_root_current + name

    # Check for existing LevelSequence and delete it to avoid message dialog when creating asset which exists
    if unreal.EditorAssetLibrary.does_asset_exist(level_sequence_path):
        unreal.log("  Deleting existing old LevelSequence: " + level_sequence_path)
        unreal.EditorAssetLibrary.delete_asset(level_sequence_path)

    # Generate LevelSequence, either via template (HDRI, camera movement) or from scratch
    if hdri_name is not None:
        # Duplicate template HDRI LevelSequence
        level_name = unreal.GameplayStatics.get_current_level_name(unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world())
        #level_name = unreal.EditorLevelUtils.get_levels(unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world())[0].get_name()
        level_sequence_hdri_template = level_sequence_hdri_prefix + level_name
        if not unreal.EditorAssetLibrary.does_asset_exist(level_sequence_hdri_template):
            unreal.log_error("Cannot find LevelSequence HDRI template: " + level_sequence_hdri_template)
            return False
        level_sequence = unreal.EditorAssetLibrary.duplicate_asset(level_sequence_hdri_template, level_sequence_path)
        hdri_path = f"{hdri_root}{hdri_name}{hdri_suffix}"
        unreal.log(f"  Loading HDRI: {hdri_path}")
        hdri_object = unreal.load_object(None, hdri_path)
        if hdri_object is None:
            unreal.log_error("Cannot load HDRI")
            return False

        # Set loaded HDRI as Skylight cubemap in sequencer
        for binding in level_sequence.get_possessables():
            binding_name = binding.get_name()
            if (binding_name == "Skylight"):
                for track in binding.get_tracks():
                    for section in track.get_sections():
                        for channel in section.get_all_channels():
                            channel.set_default(hdri_object)
    elif camera_movement_type != "Default":
        # Duplicate template camera LevelSequence
        level_sequence_camera_template = f"{camera_root}LS_Camera_{camera_movement_type}"
        if not unreal.EditorAssetLibrary.does_asset_exist(level_sequence_camera_template):
            unreal.log_error("Cannot find LevelSequence camera template: " + level_sequence_camera_template)
            return False
        level_sequence = unreal.EditorAssetLibrary.duplicate_asset(level_sequence_camera_template, level_sequence_path)
    else:
        level_sequence = unreal.AssetTools.create_asset(asset_tools, asset_name = name, package_path = level_sequences_root_current, asset_class = unreal.LevelSequence, factory = unreal.LevelSequenceFactoryNew())

    # Set frame rate to 30fps
    frame_rate = unreal.FrameRate(numerator = 30, denominator = 1)
    level_sequence.set_display_rate(frame_rate)

    camera_binding = None
    camera_component_binding = None
    cameraroot_binding = None

    if camera_movement_type == "Default":
        # Create new camera
        target_camera_pose = camera_pose

        if camera_animations is not None:
            follow_camera = camera_animations["info"]["config"]["follow"]
            if follow_camera:
                target_camera_pose = None # do not create camera transform track for follow camera

        (camera_binding, camera_component_binding, camera_cut_section) = add_static_camera(level_sequence, camera_actor, target_camera_pose, camera_hfov)
    else:
        # Use existing camera from LevelSequence template
        master_track = level_sequence.get_master_tracks()[0]
        camera_cut_section = master_track.get_sections()[0]
        camera_cut_section.set_start_frame(-WARMUP_FRAMES) # Use negative frames as warmup frames

        if camera_movement_type.startswith("Zoom") or camera_movement_type.startswith("Orbit"):
            # Add camera transform track and set static camera pose
            for binding in level_sequence.get_possessables():
                binding_name = binding.get_name()
                if binding_name == "BE_CineCameraActor_Blueprint":
                    add_transform_track(binding, camera_pose)

                if binding_name == "CameraComponent":
                    # Set HFOV
                    focal_length = get_focal_length(camera_actor.get_cine_camera_component(), camera_hfov)
                    binding.get_tracks()[0].get_sections()[0].get_all_channels()[0].set_default(focal_length)

                if camera_movement_type.startswith("Zoom"):
                    if binding_name == "CameraComponent":
                        # Set end focal length keyframe time to end of sequence
                        change_binding_end_keyframe_times(binding, sequence_frames)
                elif camera_movement_type.startswith("Orbit"):
                    if binding_name == "BE_CameraRoot":
                        cameraroot_binding = binding
                        change_binding_end_keyframe_times(binding, sequence_frames)

    # Setup time-of-day if specified
    if time_of_day is not None:
        setup_time_of_day(level_sequence, time_of_day, sunsky_actor)

    if camera_animations is not None:
        # Add camera animation keyframes
        cameraroot_binding = None
        cameraroot_actor = camera_actor.get_attach_parent_actor()
        if cameraroot_actor is not None:
            cameraroot_binding = level_sequence.add_possessable(cameraroot_actor) # Add camera root actor to level sequence
        else:
            unreal.log_warning("Cannot find camera root actor for CineCameraActor. This is OK for BE_IBL.")

        # Check for camera type
        static_world_location = camera_animations["info"]["config"]["static_world_location"]
        look_at_camera = camera_animations["info"]["config"]["look_at"]
        follow_camera = camera_animations["info"]["config"]["follow"]
        if look_at_camera and not static_world_location:
            setup_lookat_camera(camera_animations, sequence_name, camera_binding)
        elif follow_camera:
            setup_follow_camera(level_sequence, camera_binding, camera_operator_actor, camera_animations, sequence_name)

        sensor_width = float(camera_animations["info"]["config"]["sensor_width"])
        if sensor_width > 0:
            sensor_height = float(camera_animations["info"]["config"]["sensor_height"])
            setup_camera_sensor(camera_component_binding, sensor_width, sensor_height)

        if "camera_shake" in camera_animations[name]["info"]:
            camera_shake_name = camera_animations[name]["info"]["camera_shake"]
            camera_shake_scale = camera_animations[name]["info"]["camera_shake_scale"]
            start_offset = camera_animations[name]["info"]["camera_shake_start_offset"]
            status = setup_camera_shake(camera_component_binding, camera_shake_name, camera_shake_scale, sequence_frames, start_offset)
            if status == False:
                return False

        if not follow_camera and not static_world_location:
            status = add_camera_animation(camera_animations, level_sequence, sequence_name, cameraroot_binding, camera_binding, sequence_frames)

            if status == False:
                return False

        status = add_camera_hfov_animation(camera_animations, sequence_name, camera_component_binding, camera_actor)
        if status == False:
            return False

    elif (cameraroot_yaw is not None) or (cameraroot_location is not None):
        cameraroot_actor = camera_actor.get_attach_parent_actor()
        if cameraroot_actor is None:
            unreal.log_error("Cannot find camera root actor for CineCameraActor")
            return False

        transform_channels = None
        if cameraroot_binding is None:
            # Add camera root actor to level sequence
            cameraroot_binding = level_sequence.add_possessable(cameraroot_actor)
            transform_track = cameraroot_binding.add_track(unreal.MovieScene3DTransformTrack)
            transform_section = transform_track.add_section()
            transform_section.set_start_frame_bounded(False)
            transform_section.set_end_frame_bounded(False)
            transform_channels = transform_section.get_all_channels()
            if (cameraroot_yaw is not None):
                transform_channels[5].set_default(cameraroot_yaw) # yaw
            else:
                transform_channels[5].set_default(0.0)
        else:
            if cameraroot_yaw is not None:
                # Add cameraroot to existing keyframed yaw values
                transform_channels = cameraroot_binding.get_tracks()[0].get_sections()[0].get_all_channels()
                yaw_channel = transform_channels[5]
                channel_keys = yaw_channel.get_keys()
                for key in channel_keys:
                    key.set_value(key.get_value() + cameraroot_yaw)

        if cameraroot_location is None:
            cameraroot_location = cameraroot_actor.get_actor_location() # Default camera root location is not automatically taken from level actor when adding track via Python

        transform_channels[0].set_default(cameraroot_location.x)
        transform_channels[1].set_default(cameraroot_location.y)
        transform_channels[2].set_default(cameraroot_location.z)

    """
    # Get end frame from body sequence
    body_object = unreal.load_object(None, body_path)
    # Python Alembic import bug in 4.27.1 makes cache longer by one frame
    # Example:
    #   126 frame sequence gets imported as end_frame=127
    #   Last frame for Movie Render Queue is (end_frame-1)
    #   We need to set end_frame 126 to ensure that [0, 125] is rendered out.
    end_frame = body_object.end_frame - 1
    """
    end_frame = sequence_frames
    camera_cut_section.set_end_frame(end_frame)
    level_sequence.set_playback_start(-WARMUP_FRAMES) # Use negative frames as warmup frames
    level_sequence.set_playback_end(end_frame)

    # Add ground truth logger if available and keyframe sequencer frame numbers into Frame variable
    if ground_truth_logger_actor is not None:
        logger_binding = level_sequence.add_possessable(ground_truth_logger_actor)

        frame_track = logger_binding.add_track(unreal.MovieSceneIntegerTrack)
        frame_track.set_property_name_and_path('Frame', 'Frame')
        frame_track_section = frame_track.add_section()
        frame_track_section.set_range(-WARMUP_FRAMES, end_frame)
        frame_track_channel = frame_track_section.get_all_channels()[0]
        if WARMUP_FRAMES > 0:
            frame_track_channel.add_key(time=unreal.FrameNumber(-WARMUP_FRAMES), new_value=-1)

        for frame_number in range (0, end_frame):
            frame_track_channel.add_key(time=unreal.FrameNumber(frame_number), new_value=frame_number)

        # Add level sequence name
        sequence_name_track = logger_binding.add_track(unreal.MovieSceneStringTrack)
        sequence_name_track.set_property_name_and_path('SequenceName', 'SequenceName')
        sequence_name_section = sequence_name_track.add_section()
        sequence_name_section.set_start_frame_bounded(False)
        sequence_name_section.set_end_frame_bounded(False)

        sequence_name_section.get_all_channels()[0].set_default(name)

    for sequence_body_index, sequence_body in enumerate(sequence_bodies):

        body_object = unreal.load_object(None, sequence_body.body_path)
        if body_object is None:
            unreal.log_error(f"Cannot load body asset: {sequence_body.body_path}")
            return False

        animation_start_frame = -sequence_body.start_frame
        animation_end_frame = sequence_frames

        # Hair
        groom_asset = None
        groom_binding = None
        groom_material = None
        if sequence_body.hair_path is not None:
            # Reference: /Script/HairStrandsCore.GroomAsset'/Engine/PS/Bedlam/Hair/VineFX/vinefx_groom_01-1_curly-M.vinefx_groom_01-1_curly-M'
            groom_asset = unreal.EditorAssetLibrary.load_asset(f"GroomAsset'{sequence_body.hair_path}'")
            if not groom_asset:
                unreal.log_error(f"Cannot load GroomAsset: {sequence_body.hair_path}")
                return False

            groom_root = sequence_body.hair_path.rsplit("/", maxsplit=1)[0]
            groom_name = sequence_body.hair_path.rsplit("/", maxsplit=1)[1]
            binding_name = f"{groom_name}_{sequence_body.subject}"
            groom_binding_path = f"{groom_root}/Bindings/GeometryCache/{sequence_body.subject}/{binding_name}"
            # Reference: /Script/HairStrandsCore.GroomBindingAsset'/Engine/PS/Bedlam/Hair/VineFX/Bindings/GeometryCache/vinefx_groom_01-1_curly-M_rp_aaron_posed_002.vinefx_groom_01-1_curly-M_rp_aaron_posed_002'
            unreal.log_warning(f"{groom_binding_path}")
            groom_binding = unreal.EditorAssetLibrary.load_asset(f"GroomBindingAsset'{groom_binding_path}'")
            if not groom_binding:
                unreal.log_error(f"Cannot load GroomBindingAsset: {groom_binding_path}")
                return False

            groom_material = unreal.EditorAssetLibrary.load_asset(f"MaterialInstance'{sequence_body.haircolor_path}'")
            if not groom_material:
                unreal.log_error(f"Cannot load Groom MaterialInstance: {sequence_body.haircolor_path}")
                return False

        # Check if we use clothing overlay textures instead of textured clothing geometry
        if sequence_body.texture_clothing_overlay is not None:

            # Set Soft Object Paths to textures
            texture_body_path = f"Texture2D'{texture_body_root}/{sequence_body.texture_body}.{sequence_body.texture_body}'"
            texture_clothing_overlay_path = f"Texture2D'{texture_clothing_overlay_root}/{sequence_body.texture_clothing_overlay}.{sequence_body.texture_clothing_overlay}'"

            add_geometry_cache(level_sequence, sequence_body_index, "body", animation_start_frame, animation_end_frame, body_object, groom_asset, groom_binding, groom_material, sequence_body.x, sequence_body.y, sequence_body.z, sequence_body.yaw, sequence_body.pitch, sequence_body.roll, None, texture_body_path, texture_clothing_overlay_path)

        else:
            # Add body
            material = None
            if sequence_body.texture_body is not None:
                if sequence_body.shoe is not None:
                    material_asset_path = f"{material_shoe_root}/{sequence_body.shoe}/MI_{sequence_body.texture_body}_{sequence_body.shoe}"
                else:
                    material_asset_path = f"{material_body_root}/MI_{sequence_body.texture_body}"

                material = unreal.EditorAssetLibrary.load_asset(f"MaterialInstanceConstant'{material_asset_path}'")
                if not material:
                    unreal.log_error(f"Cannot load material: {material_asset_path}")
                    return False

            add_geometry_cache(level_sequence, sequence_body_index, "body", animation_start_frame, animation_end_frame, body_object, groom_asset, groom_binding, groom_material, sequence_body.x, sequence_body.y, sequence_body.z, sequence_body.yaw, sequence_body.pitch, sequence_body.roll, material)

            # Add clothing if available
            if sequence_body.clothing_path is not None:
                clothing_object = unreal.load_object(None, sequence_body.clothing_path)
                if clothing_object is None:
                    unreal.log_error(f"Cannot load clothing asset: {sequence_body.clothing_path}")
                    return False

                material = None

                if sequence_body.texture_clothing is not None:
                    outfit_name = sequence_body.texture_clothing.split("_texture_")[0] # Example: gr_aaron_009_texture_01 => gr_aaron_009
                    material_asset_path = f"{material_clothing_root}/{outfit_name}/MI_{sequence_body.texture_clothing}"
                    material = unreal.EditorAssetLibrary.load_asset(f"MaterialInstanceConstant'{material_asset_path}'")
                    if not material:
                        unreal.log_error(f"Cannot load clothing material: {material_asset_path}")
                        return False

                add_geometry_cache(level_sequence, sequence_body_index, "clothing", animation_start_frame, animation_end_frame, clothing_object, None, None, None, sequence_body.x, sequence_body.y, sequence_body.z, sequence_body.yaw, sequence_body.pitch, sequence_body.roll, material)


            # Camera target handling
            if sequence_body_index == 0:
                if camera_animations is not None:
                    if camera_target_actor is None:
                        unreal.log_error(f"Camera target actor BE_CameraTarget not found in level")
                        return False

                    if "look_at_target" in camera_animations["info"]["config"]:
                        lookat_target = camera_animations["info"]["config"]["look_at_target"]
                        if lookat_target == "body_0":
                            # Add animation for camera tracking of first body if activated
                            skeletal_mesh_actor_binding = add_animation(level_sequence, animation_start_frame, animation_end_frame, sequence_body.animation_path, sequence_body.x, sequence_body.y, sequence_body.z, sequence_body.yaw, sequence_body.pitch, sequence_body.roll)

                            if "look_at_bodypart" in camera_animations[sequence_name]["info"]:
                                attach_socket_name = camera_animations[sequence_name]["info"]["look_at_bodypart"]
                            else:
                                attach_socket_name = "spine1"
                                follow_static_location = camera_animations["info"]["config"]["follow_static_location"]
                                static_world_location = camera_animations["info"]["config"]["static_world_location"]
                                if follow_static_location or static_world_location:
                                    attach_socket_name = "pelvis" # target pelvis for static camera locations for better framing when using long lenses

                            attach_camera_target(level_sequence, skeletal_mesh_actor_binding, attach_socket_name, camera_target_actor)
                        elif lookat_target == "cameraroot":
                            # Track fixed world location at cameraroot ground location
                            cameraroot = camera_animations[sequence_name]["keyframes"][0]["cameraroot"]
                            cameraroot_ground_world = camera_animations[sequence_name]["info"]["ground_height_world"]
                            camera_target_actor_location = unreal.Vector(cameraroot["x"], cameraroot["y"], cameraroot_ground_world)
                            attach_camera_target(level_sequence, None, None, camera_target_actor, camera_target_actor_location)
                        else:
                            unreal.log_error(f"Unsupported lookat target: {lookat_target}")

    unreal.EditorAssetLibrary.save_asset(level_sequence.get_path_name())

    return True

def cleanup_mask_layers():
    # Remove added layers used for segmentation mask naming

    # If World Partition system is used for the current map (CitySample), the layer system is not available and we used folder names for tagging the masks.
    # Note that we need to keep these empty folders so that the spawned GeometryCache actors from the LevelSequences will later show up under those.
    layer_subsystem = unreal.get_editor_subsystem(unreal.LayersSubsystem)
    layer_names = layer_subsystem.add_all_layer_names_to()
    if len(layer_names) > 0:
        for layer_name in layer_names:
            if str(layer_name).startswith("be_actor"):
                layer_subsystem.delete_layer(layer_name)

    return

######################################################################
# Main
######################################################################
if __name__ == '__main__':
    unreal.log("============================================================")
    unreal.log("Running: %s" % __file__)

    if len(sys.argv) >= 2:
        csv_path = sys.argv[1]

    camera_movement_type = "Default"
    if len(sys.argv) >= 3:
        camera_movement_type = sys.argv[2]

    sequence_index_min = None
    if len(sys.argv) >= 4:
        sequence_index_min = int(sys.argv[3])

    sequence_index_max = None
    if len(sys.argv) >= 5:
        sequence_index_max = int(sys.argv[4])

    camera_animations = None
    if camera_movement_type == "Default":

        # Check for presence of be_camera_animations.json file
        # If be_camera_animations_depth.json (fully keyframed camera pose) is existing then this will be used instead of be_camera_animations.json
        camera_animation_depth_filename = camera_animation_filename.replace(".json", "_depth.json")
        camera_movement_path = Path(csv_path).parent / camera_animation_depth_filename
        if not camera_movement_path.is_file():
            camera_movement_path = Path(csv_path).parent / camera_animation_filename

        if camera_movement_path.is_file():
            unreal.log(f"Using camera animation definition: {camera_movement_path}")
            with open(camera_movement_path, "r") as f:
                camera_animations = json.load(f)

    start_time = time.perf_counter()

    # Find CineCameraActor and BE_GroundTruthLogger in current map
    actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors() # deprecated: unreal.EditorLevelLibrary.get_all_level_actors()
    camera_actor = None
    ground_truth_logger_actor = None
    camera_target_actor = None
    camera_operator_actor = None
    sunsky_actor = None
    for actor in actors:
        if actor.static_class() == unreal.CineCameraActor.static_class():
            camera_actor = actor
        elif actor.get_class().get_name() == "BE_GroundTruthLogger_C":
            ground_truth_logger_actor = actor
        elif actor.get_actor_label() == "BE_CameraTarget":
            camera_target_actor = actor
        elif actor.get_class().get_name() == "BE_CameraOperator_C":
            camera_operator_actor = actor
        elif actor.get_class().get_name() == "SunSky_C":
            sunsky_actor = actor
        elif actor.get_class().get_name() == "BE_SunSky_C":
            sunsky_actor = actor

    success = True

    if camera_actor is None:
        unreal.log_error("Cannot find CineCameraActor in current map")
        unreal.log_error(f"LevelSequence generation failed. Total time: {(time.perf_counter() - start_time):.1f}s")
        sys.exit(1)


    # Generate LevelSequences for defined sequences in csv file
    csv_rows= None
    with open(csv_path, mode="r") as csv_file:
        csv_reader = csv.DictReader(csv_file)
        csv_rows = list(csv_reader) # Convert to list of rows so that we can look ahead, this will skip header

    sequence_bodies = []

    sequence_name = None
    sequence_frames = 0
    hdri_name = None
    camera_hfov = None
    camera_pose = None
    cameraroot_yaw = None
    cameraroot_location = None
    time_of_day = None
    sequence_index = None
    skip_sequence = False

    # Get number of sequences
    total_items = 0
    for row in csv_rows:
        if row["Type"] == "Group":
            total_items += 1

    text_label = "Creating BEDLAM LevelSequences"
    items_processed = 1

    with unreal.ScopedSlowTask(total_items, text_label) as slow_task:
        slow_task.make_dialog(True) # Makes the dialog visible, if it isn't already

        for row_index, row in enumerate(csv_rows):

            if row["Type"] == "Comment":
                continue

            if row["Type"] == "Group":
                camera_pose = ActorPose(float(row["X"]), float(row["Y"]), float(row["Z"]), float(row["Yaw"]), float(row["Pitch"]), float(row["Roll"]))

                # Parse additional group configuration
                values = row["Comment"].split(";")
                dict_keys = []
                dict_values = []
                for value in values:
                    dict_keys.append(value.split("=")[0])
                    dict_values.append(value.split("=")[1])
                group_config = dict(zip(dict_keys, dict_values))
                sequence_name = group_config["sequence_name"]
                sequence_frames = int(group_config["frames"])

                # Get sequence index from sequence name ("seq_000123" => 123)
                if "_" in sequence_name:
                    sequence_index = int(sequence_name.rsplit("_", maxsplit=1)[1])
                    # Check if we skip this sequence
                    skip_sequence = False
                    if sequence_index_min is not None:
                        if sequence_index < sequence_index_min:
                            skip_sequence = True

                    if sequence_index_max is not None:
                        if sequence_index > sequence_index_max:
                            skip_sequence = True

                    if skip_sequence:
                        unreal.log(f"  Skipping level sequence: {sequence_name}")
                        continue

                # Check if HDRI was specified
                if "hdri" in group_config:
                    hdri_name = group_config["hdri"]
                else:
                    hdri_name = None

                # Check if camera HFOV was specified
                if "camera_hfov" in group_config:
                    camera_hfov = float(group_config["camera_hfov"])
                else:
                    camera_hfov = None

                # Check if time-of-day was specified
                if "time" in group_config:
                    if sunsky_actor is None:
                        unreal.log_error("ERROR: time-of-day specified in CSV but no SunSky actor in current level")
                        success = False
                        break

                    time_of_day = float(group_config["time"])

                # Only use cameraroot yaw/location from csv if we are not using camera animations
                if camera_animations is None:
                    if "cameraroot_yaw" in group_config:
                        cameraroot_yaw = float(group_config["cameraroot_yaw"])
                    else:
                        cameraroot_yaw = None

                    if "cameraroot_x" in group_config:
                        cameraroot_x =float(group_config["cameraroot_x"])
                        cameraroot_y =float(group_config["cameraroot_y"])
                        cameraroot_z =float(group_config["cameraroot_z"])
                        cameraroot_location = unreal.Vector(cameraroot_x, cameraroot_y, cameraroot_z)
                    else:
                        cameraroot_location = None

                unreal.log(f"  Generating level sequence: {sequence_name}, frames={sequence_frames}, hdri={hdri_name}, camera_hfov={camera_hfov}")
                sequence_bodies = []

                continue

            if row["Type"] == "Body":
                if skip_sequence:
                    continue

                index = int(row["Index"])
                body = row["Body"]


                x = float(row["X"])
                y = float(row["Y"])
                z = float(row["Z"])
                yaw = float(row["Yaw"])
                pitch = float(row["Pitch"])
                roll = float(row["Roll"])

                # Parse additional body configuration
                values = row["Comment"].split(";")
                dict_keys = []
                dict_values = []
                for value in values:
                    dict_keys.append(value.split("=")[0])
                    dict_values.append(value.split("=")[1])
                body_config = dict(zip(dict_keys, dict_values))
                start_frame = 0
                if "start_frame" in body_config:
                    start_frame = int(body_config["start_frame"])

                texture_body = None
                if "texture_body" in body_config:
                    texture_body = body_config["texture_body"]

                texture_clothing = None
                if "texture_clothing" in body_config:
                    texture_clothing = body_config["texture_clothing"]

                texture_clothing_overlay = None
                if "texture_clothing_overlay" in body_config:
                    texture_clothing_overlay = body_config["texture_clothing_overlay"]

                hair_path = None
                haircolor_path = None
                if "hair" in body_config:
                    hair_type = body_config["hair"]
                    hair_path = f"{hair_root}{hair_type}"
                    haircolor = body_config["haircolor"]
                    haircolor_path = f"{material_hair_root}/MI_Hair_{haircolor}"

                shoe = None
                if "shoe" in body_config:
                    shoe = body_config["shoe"]

                subject = "undefined"
                animation_id = "undefined"
                if body.startswith("moyo"):
                    # moyo_Akarna_Dhanurasana-a
                    subject = body.split("_", maxsplit=1)[0]
                    animation_id = body
                else:
                    # rp_aaron_posed_002_1234
                    subject = body.rsplit("_", maxsplit=1)[0]
                    animation_id = body.rsplit("_", maxsplit=1)[1]

                # Body: GeometryCache'/Engine/PS/Bedlam/SMPLX/it_4001_XL/it_4001_XL_2400.it_4001_XL_2400'
                # Clothing: GeometryCache'/Engine/PS/Bedlam/Clothing/it_4001_XL/it_4001_XL_2400_clo.it_4001_XL_2400_clo'

                body_path = f"GeometryCache'{body_root}{subject}/{body}.{body}'"

                have_body = unreal.EditorAssetLibrary.does_asset_exist(body_path)
                if not have_body:
                    unreal.log_error("No asset found for body path: " + body_path)
                    success = False
                    break

                unreal.log("    Processing body: " + body_path)

                clothing_path = None
                if texture_clothing is not None:
                    clothing_path = f"GeometryCache'{clothing_root}{subject}/{body}_clo.{body}_clo'"

                    have_clothing = unreal.EditorAssetLibrary.does_asset_exist(clothing_path)
                    if not have_clothing:
                        unreal.log_error("No asset found for clothing path: " + clothing_path)
                        success = False
                        break

                    unreal.log("    Clothing: " + clothing_path)



                # AnimSequence'/Engine/PS/Bedlam/SMPLX_LH_animations/it_4001_XL/it_4001_XL_2400_Anim.it_4001_XL_2400_Anim'
                animation_path = f"AnimSequence'{animation_root}{subject}/{body}_Anim.{body}_Anim'"

                sequence_body = SequenceBody(subject, body_path, clothing_path, hair_path, animation_path, x, y, z, yaw, pitch, roll, start_frame, texture_body, texture_clothing, texture_clothing_overlay, haircolor_path, shoe)
                sequence_bodies.append(sequence_body)

                # Check if body was last item in current sequence
                add_sequence = False
                if index >= (len(csv_rows) - 1):
                    add_sequence = True
                elif csv_rows[row_index + 1]["Type"] != "Body":
                    add_sequence = True

                if add_sequence:

                    # Update progress dialog
                    if slow_task.should_cancel():
                        success = False
                        break
                    desc = f"{text_label} [{items_processed}/{total_items}]"
                    slow_task.enter_progress_frame(1, desc) # Advance progress by one item and update dialog text

                    success = add_level_sequence(sequence_name, camera_actor, camera_pose, ground_truth_logger_actor, camera_target_actor, camera_operator_actor, sequence_bodies, sequence_frames, hdri_name, camera_hfov, camera_movement_type, camera_animations, cameraroot_yaw, cameraroot_location, time_of_day=time_of_day, sunsky_actor=sunsky_actor)
                    cleanup_mask_layers() # Remove added layers used for segmentation mask naming
                    if not success:
                        break

                    items_processed += 1

    if success:
        unreal.log(f"LevelSequence generation finished. Total time: {(time.perf_counter() - start_time):.1f}s")
        sys.exit(0)
    else:
        unreal.log_error(f"LevelSequence generation failed. Total time: {(time.perf_counter() - start_time):.1f}s")
        sys.exit(1)
