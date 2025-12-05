# Copyright (c) 2025 Max Planck Society
# License: https://bedlam2.is.tuebingen.mpg.de/license.html
#
# Export world location and size information of all BE_Stage actors to CSV
#
from pathlib import Path
import sys
import unreal

OUTPUT_ROOT = Path(r"C:\bedlam\render\config\locations")

def export_occlusion_mask(actor, image_path):
    dynamic_mesh = actor.get_dynamic_mesh_component().get_dynamic_mesh()
    bake_types = unreal.Array(unreal.GeometryScriptBakeTypeOptions)
    bake_types.append(unreal.GeometryScriptBakeTypeOptions(bake_type=unreal.GeometryScriptBakeTypes.VERTEX_COLOR))
    bake_options = unreal.GeometryScriptBakeTextureOptions(resolution=unreal.GeometryScriptBakeResolution.RESOLUTION128,
                                                           bit_depth=unreal.GeometryScriptBakeBitDepth.CHANNEL_BITS8,
                                                           samples_per_pixel=unreal.GeometryScriptBakeSamplesPerPixel.SAMPLE1,
                                                           filtering_type = unreal.GeometryScriptBakeFilteringType.BOX,
                                                           projection_distance = 3.0,
                                                           projection_in_world_space = False)

    textures = unreal.GeometryScript_Bake.bake_texture(target_mesh=dynamic_mesh,
                                                       target_transform=unreal.Transform(),
                                                       target_options=unreal.GeometryScriptBakeTargetMeshOptions(),
                                                       source_mesh=dynamic_mesh,
                                                       source_transform=unreal.Transform(),
                                                       source_options=unreal.GeometryScriptBakeSourceMeshOptions(),
                                                       bake_types=bake_types,
                                                       bake_options=bake_options,
                                                       debug=None)

    num_textures = len(textures)
    if num_textures != 1:
        unreal.log_error(f"Invalid number of bake textures (want: 1): {num_textures}")
        return False

    texture = textures[0]
    export_options = unreal.ImageWriteOptions(format = unreal.DesiredImageFormat.PNG,
                                              compression_quality = 0,
                                              overwrite_file=True,
                                              async_=False)
    texture.export_to_disk(str(image_path), export_options)
    return True

def export_data():

    actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()
    stage_actors = []
    for actor in actors:
        if actor.get_class().get_name() == "BE_Stage_C":
            actor_label = actor.get_actor_label()
            stage_actors.append( (actor_label, actor) )

    if len(stage_actors) == 0:
        unreal.log_error(f"No BE_Stage actors found.")
        return False

    # Sort by actor label
    stage_actors = sorted(stage_actors, key=lambda x: x[0])

    # Use current level name as output name
    current_level = unreal.EditorLevelUtils.get_levels(unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world())[0]
    level_name = unreal.SystemLibrary.get_outer_object(current_level).get_name()
    output_name = f"{level_name}.csv"

    target_path = OUTPUT_ROOT / level_name / f"{level_name}.csv"
    print(f"Exporting data: {target_path}")
    if not target_path.parent.exists():
        target_path.parent.mkdir(parents=True, exist_ok=True)

    with open(target_path, "w") as f:
        f.write("name,x,y,z,yaw,size_x,size_y,camera_radius_max,camera_height_min,camera_height_max\n")

        for (actor_label, actor) in stage_actors:
            location = actor.get_actor_location()
            rotation = actor.get_actor_rotation()
            size_x = actor.get_editor_property("SizeX")
            size_y = actor.get_editor_property("SizeY")
            camera_radius_max = actor.get_editor_property("CameraRadiusMax")
            camera_height_min = actor.get_editor_property("CameraHeightMin")
            camera_height_max = actor.get_editor_property("CameraHeightMax")
            line = f"{actor_label},{location.x},{location.y},{location.z},{rotation.yaw},{size_x},{size_y},{camera_radius_max},{camera_height_min},{camera_height_max}"
            print(f"  Processing: {line}")
            f.write(f"{line}\n")

    # Export occlusion masks
    target_path_root = OUTPUT_ROOT / level_name
    print(f"Exporting occlusion masks: {target_path_root}")
    for (actor_label, actor) in stage_actors:
        occluders_box = actor.get_editor_property("OccludersBox")
        occluders_sphere = actor.get_editor_property("OccludersSphere")

        # We only export mask if it has defined occluders
        if (len(occluders_box) == 0) and (len(occluders_sphere) == 0):
            print(f"  Processing: {actor_label}: No occlusion defined")
            continue

        stage_index = actor_label.rsplit("_", maxsplit=1)[1]
        image_name = f"{level_name}_stage_{stage_index}.png"
        image_path = target_path_root / image_name

        print(f"  Processing: {actor_label}: {image_path}")
        success = export_occlusion_mask(actor, image_path)
        if not success:
            unreal.log_error("Cannot export occlusion mask.")
            return False

    return True

if __name__ == '__main__':
    unreal.log("============================================================")
    unreal.log("Running: %s" % __file__)

    success = export_data()

    if success:
        unreal.log(f"Stage export finished.")
        sys.exit(0)
    else:
        unreal.log_error(f"Stage export failed.")
        sys.exit(1)
