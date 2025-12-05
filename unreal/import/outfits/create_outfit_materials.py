# Copyright (c) 2025 Max Planck Society
# License: https://bedlam2.is.tuebingen.mpg.de/license.html
#
# Generate top/bottom outfit Material Instances
#

import unreal

data_root_unreal = "/Engine/PS/Meshcapade/SMPLX"

master_material_name = f"/Engine/PS/Meshcapade/SMPLX/M_SMPLX_Clothing_MOYO"
material_prefix = "moyo"
TEXTURES_TOP=["Female_Top_ALB_0004", "Female_Top_ALB_0005", "Female_Top_ALB_0008", "Female_Top_ALB_0010", "Female_Top_ALB_0012a", "Female_Top_ALB_0012b", "Female_Top_ALB_0012c", "Female_Top_ALB_0012d", "Female_Top_ALB_0012e", "Female_Top_ALB_0012f", "Female_Top_ALB_0013"]
TEXTURES_BOTTOM=["Female_Bottom_ALB_0008", "Female_Bottom_ALB_0009"]

def create_materials(master_material, material_prefix, textures_top, textures_bottom):
    outfit_index = 0
    texture_root = f"{data_root_unreal}/Textures"
    for texture_top in textures_top:

        texture_asset_path = f"{texture_root}/{texture_top}"
        texture_top_asset = unreal.EditorAssetLibrary.load_asset(f"Texture2D'{texture_asset_path}'")
        if not texture_top_asset:
            unreal.log_error(f"Cannot load texture: {texture_asset_path}")
            return False

        for texture_bottom in textures_bottom:

            texture_asset_path = f"{texture_root}/{texture_bottom}"
            texture_bottom_asset = unreal.EditorAssetLibrary.load_asset(f"Texture2D'{texture_asset_path}'")
            if not texture_bottom_asset:
                unreal.log_error(f"Cannot load texture: {texture_asset_path}")
                return False

            material_instance_name = f"MI_{material_prefix}_outfit_{outfit_index:04d}"
            outfit_index += 1
            material_instance_root = f"{data_root_unreal}/Outfits"
            material_instance_path = f"{material_instance_root}/{material_instance_name}"

            if unreal.EditorAssetLibrary.does_asset_exist(material_instance_path):
                unreal.log("  Skipping. MaterialInstance exists: " + material_instance_path)
                return

            unreal.log(f"Creating MaterialInstance: {material_instance_path}")
            material_instance = unreal.AssetToolsHelpers.get_asset_tools().create_asset(asset_name=material_instance_name, package_path=material_instance_root, asset_class=unreal.MaterialInstanceConstant, factory=unreal.MaterialInstanceConstantFactoryNew())
            unreal.MaterialEditingLibrary.set_material_instance_parent(material_instance, master_material)
            unreal.MaterialEditingLibrary.set_material_instance_texture_parameter_value(material_instance, 'ClothingTopTexture', texture_top_asset)
            unreal.MaterialEditingLibrary.set_material_instance_texture_parameter_value(material_instance, 'ClothingBottomTexture', texture_bottom_asset)

    return

######################################################################
# Main
######################################################################
if __name__ == "__main__":
    unreal.log("============================================================")
    unreal.log("Running: %s" % __file__)

# Load master material
master_material = unreal.EditorAssetLibrary.load_asset(f"Material'{master_material_name}'")
if not master_material:
    unreal.log_error('Cannot load master material: ' + master_material_name)
else:
    create_materials(master_material, material_prefix, TEXTURES_TOP, TEXTURES_BOTTOM)
