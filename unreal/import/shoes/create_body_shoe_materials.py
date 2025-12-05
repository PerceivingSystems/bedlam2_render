# Copyright (c) 2025 Max Planck Society
# License: https://bedlam2.is.tuebingen.mpg.de/license.html
#
# Generate body+shoe MaterialInstances for all available body texture and shoe types combinations
#

from pathlib import PurePath
import unreal

data_root_unreal_bodytextures = "/Engine/PS/Meshcapade/SMPLX/Textures/bald"
data_root_unreal_shoes = "/Engine/PS/Bedlam/Shoes"

master_material_name = f"/Engine/PS/Bedlam/Core/Materials/M_SMPLX_Shoe"

def create_materials(data_root_unreal_bodytextures, data_root_unreal_shoes, master_material):

    shoe_materials_root = f"{data_root_unreal_shoes}/Materials"
    unreal.log(f"MaterialInstance target folder: {shoe_materials_root}")
    shoe_texture_root = f"{data_root_unreal_shoes}/Textures"


    # Get available body texture names from texture folder subdir names
    texture_body_names = []
    assets = unreal.EditorAssetLibrary.list_assets(data_root_unreal_bodytextures, recursive=False, include_folder=False)
    for asset_path in assets:
        texture_body_name = unreal.Paths.get_base_filename(asset_path)
        texture_body_names.append(texture_body_name)

    # Get available shoe names from texture folder subdir names
    shoe_names = []

    assets = unreal.EditorAssetLibrary.list_assets(shoe_texture_root, recursive=False, include_folder=True)
    # /Engine/PS/Bedlam/Shoes/Textures/shoe_gso_000/
    for asset_path in assets:
        shoe_name = PurePath(asset_path).name
        shoe_names.append(shoe_name)

    total_items = len(texture_body_names) * len(shoe_names)
    text_label = "Creating Body-Shoe Material Instances"
    items_processed = 1

    with unreal.ScopedSlowTask(total_items, text_label) as slow_task:
        slow_task.make_dialog(True) # Makes the dialog visible, if it isn't already

        for shoe_name in sorted(shoe_names):
            unreal.log(f"Processing: {shoe_name}")
            for texture_body_name in sorted(texture_body_names):

                if slow_task.should_cancel():
                    return False

                desc = f"{text_label} [{items_processed}/{total_items}]"
                slow_task.enter_progress_frame(1, desc) # Advance progress by one item and update dialog text


                material_instance_name = f"MI_{texture_body_name}_{shoe_name}"
                material_instance_root = f"{shoe_materials_root}/{shoe_name}"
                material_instance_path = f"{material_instance_root}/{material_instance_name}"
                if unreal.EditorAssetLibrary.does_asset_exist(material_instance_path):
                    unreal.log("  Skipping. MaterialInstance exists: " + material_instance_path)
                    continue

                # Load textures assets
                texture_asset_path = f"{data_root_unreal_bodytextures}/{texture_body_name}"
                texture_basecolor = unreal.EditorAssetLibrary.load_asset(f"Texture2D'{texture_asset_path}'")
                if not texture_basecolor:
                    unreal.log_error(f"Cannot load texture: {texture_asset_path}")
                    return False

                shoe_name_prefix = f"T_{shoe_name}"

                texture_asset_path = f"{data_root_unreal_shoes}/Textures/{shoe_name}/{shoe_name_prefix}_color"
                texture_shoebasecolor = unreal.EditorAssetLibrary.load_asset(f"Texture2D'{texture_asset_path}'")
                if not texture_shoebasecolor:
                    unreal.log_error(f"Cannot load texture: {texture_asset_path}")
                    return False

                texture_asset_path = f"{data_root_unreal_shoes}/Textures/{shoe_name}/{shoe_name_prefix}_normal"
                texture_shoenormal = unreal.EditorAssetLibrary.load_asset(f"Texture2D'{texture_asset_path}'")
                if not texture_shoenormal:
                    unreal.log_error(f"Cannot load texture: {texture_asset_path}")
                    return False

                texture_asset_path = f"{data_root_unreal_shoes}/Textures/{shoe_name}/{shoe_name_prefix}_displacement"
                texture_shoedisplacement = unreal.EditorAssetLibrary.load_asset(f"Texture2D'{texture_asset_path}'")
                if not texture_shoedisplacement:
                    unreal.log_error(f"Cannot load texture: {texture_asset_path}")
                    return False

                # Create material instance and set texture parameters
                unreal.log(f"Creating MaterialInstance: {material_instance_path}")
                material_instance = unreal.AssetToolsHelpers.get_asset_tools().create_asset(asset_name=material_instance_name, package_path=material_instance_root, asset_class=unreal.MaterialInstanceConstant, factory=unreal.MaterialInstanceConstantFactoryNew())
                unreal.MaterialEditingLibrary.set_material_instance_parent(material_instance, master_material)
                unreal.MaterialEditingLibrary.set_material_instance_texture_parameter_value(material_instance, "BaseColor", texture_basecolor)
                unreal.MaterialEditingLibrary.set_material_instance_texture_parameter_value(material_instance, "ShoeBaseColor", texture_shoebasecolor)
                unreal.MaterialEditingLibrary.set_material_instance_texture_parameter_value(material_instance, "ShoeNormal", texture_shoenormal)
                unreal.MaterialEditingLibrary.set_material_instance_texture_parameter_value(material_instance, "ShoeDisplacement", texture_shoedisplacement)

#                print(materialinstance_name)
                items_processed += 1

    # Save all generated MaterialInstances to disk
    unreal.EditorLoadingAndSavingUtils.save_dirty_packages(save_map_packages=False, save_content_packages=True)

    return True

######################################################################
# Main
######################################################################
if __name__ == "__main__":
    unreal.log("============================================================")
    unreal.log("Running: %s" % __file__)

    # Load master material
    success = False
    master_material = unreal.EditorAssetLibrary.load_asset(f"Material'{master_material_name}'")
    if not master_material:
        unreal.log_error("Cannot load master material: " + master_material_name)
    else:
        unreal.log("Creating Body-Shoe MaterialInstances")
        success = create_materials(data_root_unreal_bodytextures, data_root_unreal_shoes, master_material)

    if success:
        unreal.log("Finished [SUCCESS]")
    else:
        unreal.log_error("MaterialInstance creation failed.")
