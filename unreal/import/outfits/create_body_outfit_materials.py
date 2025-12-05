# Copyright (c) 2025 Max Planck Society
# License: https://bedlam2.is.tuebingen.mpg.de/license.html
#
# Generate Material Instances for selected textures
#

import unreal

data_root_unreal = "/Engine/PS/Meshcapade/SMPLX"

outfit_materials_path = f"{data_root_unreal}/Outfits"
outfit_material_prefix = "MI_moyo_outfit_"
num_outfit_materials = 22

material_prefix = "moyo_"

def create_material(texture, texture_index, outfit_materials):

    material_instance_name = f"MI_{material_prefix}{texture.get_name()}"
    material_instance_root = f"{data_root_unreal}/Materials"
    material_instance_path = f"{material_instance_root}/{material_instance_name}"
    if unreal.EditorAssetLibrary.does_asset_exist(material_instance_path):
        unreal.log("  Skipping. MaterialInstance exists: " + material_instance_path)
        return

    unreal.log(f"Creating MaterialInstance: {material_instance_root}/{material_instance_name}")
    material_instance = unreal.AssetToolsHelpers.get_asset_tools().create_asset(asset_name=material_instance_name, package_path=material_instance_root, asset_class=unreal.MaterialInstanceConstant, factory=unreal.MaterialInstanceConstantFactoryNew())
    parent_material = outfit_materials[texture_index % len(outfit_materials)]
    unreal.MaterialEditingLibrary.set_material_instance_parent(material_instance, parent_material)
    unreal.MaterialEditingLibrary.set_material_instance_texture_parameter_value(material_instance, 'BaseColor', texture)

    return

######################################################################
# Main
######################################################################
if __name__ == "__main__":
    unreal.log("============================================================")
    unreal.log("Running: %s" % __file__)

# Load outfit materials
outfit_materials = []
for index in range(num_outfit_materials):
    material_name = f"{outfit_material_prefix}{index:04d}"
    material_path = f"{outfit_materials_path}/{material_name}"
    outfit_material = unreal.EditorAssetLibrary.load_asset(f"MaterialInstance'{material_path}'")

    unreal.log(f"Loading outfit material instance: {material_path}")
    if not outfit_material:
        unreal.log_error("Cannot load material instance")
        break

    outfit_materials.append(outfit_material)

selection = unreal.EditorUtilityLibrary.get_selected_assets() # Loads all selected assets into memory
if len(selection) == 0:
    unreal.log_error(f"No textures selected")

texture_index = 0
for asset in selection:
    if not isinstance(asset, unreal.Texture):
        unreal.log_error(f"  Ignoring (no Texture): {asset.get_full_name()}")
        continue

    texture = asset
    unreal.log(f"  Adding: {texture.get_full_name()}")

    create_material(texture, texture_index, outfit_materials)
    texture_index += 1
