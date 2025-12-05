# Copyright (c) 2025 Max Planck Society
# License: https://bedlam2.is.tuebingen.mpg.de/license.html
#
# Import clothing textures and generate MaterialInstances
#
# TODO: Use custom master material for label textures
#
# Notes:
# + Use Unreal 5.0 or disable `Interchange Editor/Framework/Tests` plugins in 5.2
#   + Unreal 5.2+ uses Interchange Framework and will ignore `destination_name`
#     + https://docs.unrealengine.com/5.2/en-US/PythonAPI/class/AssetImportTask.html#unreal-assetimporttask

from pathlib import Path
import unreal

DATA_ROOT = r"C:\bedlam2\textures\clothing\unreal_import"
DATA_ROOT_UNREAL = "/Engine/PS/Bedlam/Clothing/Materials"
MASTER_MATERIAL_PATH = "/Engine/PS/Bedlam/Core/Materials/M_Clothing"
def import_textures(texture_paths):

    master_material = unreal.EditorAssetLibrary.load_asset(f"Material'{MASTER_MATERIAL_PATH}'")
    if not master_material:
        unreal.log_error(f"Cannot load master material: {MASTER_MATERIAL_PATH}")
        return False

    normal_texture_asset_path = None

    for texture_path in texture_paths:
        unreal.log(f"Processing {texture_path}")

        import_normal_map = True

        # Check if texture is already imported
        # gr_aaron_009\texture_01\texture_01_diffuse.png
        outfit_name = texture_path.parent.parent.name
        texture_name = texture_path.parent.name

        # Check if we have label texture
        label_texture = False
        if "texture_00" in str(texture_path):
            label_texture = True
            import_normal_map = False
            unreal.log_error("TODO: Use custom master material for label textures")
            return False

        import_tasks = []

        # Diffuse texture
        texture_asset_name = f"T_{outfit_name}_{texture_name}_diffuse"
        texture_asset_dir = f"{DATA_ROOT_UNREAL}/{outfit_name}"
        texture_asset_path = f"{texture_asset_dir}/{texture_asset_name}"

        if unreal.EditorAssetLibrary.does_asset_exist(texture_asset_path):
            unreal.log("  Skipping. Already imported: " + texture_asset_path)
        else:
            unreal.log(f"  Importing: '{texture_path}' to '{texture_asset_path}'")
            task = unreal.AssetImportTask()
            task.set_editor_property("filename", str(texture_path))
            task.set_editor_property("destination_name", texture_asset_name)
            task.set_editor_property("destination_path", texture_asset_dir)
            task.set_editor_property('save', True)
            import_tasks.append(task)

        # Normal texture
        if import_normal_map:
            normal_texture_path = texture_path.parent / texture_path.name.replace("diffuse", "normal")
            normal_texture_asset_name = f"T_{outfit_name}_{texture_name}_normal"
            normal_texture_asset_path = f"{texture_asset_dir}/{normal_texture_asset_name}"

            if unreal.EditorAssetLibrary.does_asset_exist(normal_texture_asset_path):
                unreal.log("  Skipping. Already imported: " + normal_texture_asset_path)
            else:
                unreal.log(f"  Importing: '{normal_texture_path}' to '{normal_texture_asset_path}'")
                task = unreal.AssetImportTask()
                task.set_editor_property("filename", str(normal_texture_path))
                task.set_editor_property("destination_name", normal_texture_asset_name)
                task.set_editor_property("destination_path", texture_asset_dir)
                task.set_editor_property('save', True)
                import_tasks.append(task)

        # Import diffuse and normal textures
        unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks(import_tasks)

        texture_asset = None
        # Fix label texture properties: no mipmaps, no texture compression
        if label_texture:
            texture_asset = unreal.EditorAssetLibrary.load_asset(f"Texture2D'{texture_asset_path}'")
            if not texture_asset:
                unreal.log_error(f"Cannot load texture: {texture_asset_path}")
                return False

            texture_asset.set_editor_property("mip_gen_settings", unreal.TextureMipGenSettings.TMGS_NO_MIPMAPS)
            texture_asset.set_editor_property("compression_settings", unreal.TextureCompressionSettings.TC_EDITOR_ICON)
            texture_asset.set_editor_property("filter", unreal.TextureFilter.TF_NEAREST)

            # Unreal 5.2 legacy importer (disabled Interchange Framework) imports some clothing label textures not as sRGB.
            # This is due to them being falsely auto-detected as normal map. We force sRGB texture source on import to prevent this issue.
            texture_asset.set_editor_property("srgb", True)

            unreal.EditorAssetLibrary.save_loaded_asset(texture_asset, only_if_is_dirty=False)

        # Create MaterialInstance
        material_instance_name = f"MI_{outfit_name}_{texture_name}"
        material_instance_dir = texture_asset_dir
        material_instance_path = f"{material_instance_dir}/{material_instance_name}"
        if unreal.EditorAssetLibrary.does_asset_exist(material_instance_path):
            unreal.log("  Skipping. MaterialInstance exists: " + material_instance_path)
        else:
            unreal.log(f"  Creating MaterialInstance: {material_instance_path}")
            material_instance = unreal.AssetToolsHelpers.get_asset_tools().create_asset(asset_name=material_instance_name, package_path=material_instance_dir, asset_class=unreal.MaterialInstanceConstant, factory=unreal.MaterialInstanceConstantFactoryNew())
            unreal.MaterialEditingLibrary.set_material_instance_parent(material_instance, master_material)

            if texture_asset is None:
                texture_asset = unreal.EditorAssetLibrary.load_asset(f"Texture2D'{texture_asset_path}'")
                if not texture_asset:
                    unreal.log_error(f"Cannot load texture: {texture_asset_path}")
                    return False
            unreal.MaterialEditingLibrary.set_material_instance_texture_parameter_value(material_instance, 'BaseColor', texture_asset)

            if import_normal_map:
                normal_texture_asset = unreal.EditorAssetLibrary.load_asset(f"Texture2D'{normal_texture_asset_path}'")
                if not normal_texture_asset:
                    unreal.log_error(f"Cannot load texture: {normal_texture_asset_path}")
                    return False
                unreal.MaterialEditingLibrary.set_material_instance_texture_parameter_value(material_instance, 'Normal', normal_texture_asset)

    return True

######################################################################
# Main
######################################################################
if __name__ == "__main__":
    unreal.log("============================================================")
    unreal.log("Running: %s" % __file__)

    # Build import list
    import_texture_paths = sorted(Path(DATA_ROOT).rglob("*diffuse*.png"))

    import_textures(import_texture_paths)
