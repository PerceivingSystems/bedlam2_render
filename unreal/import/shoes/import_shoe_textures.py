# Copyright (c) 2025 Max Planck Society
# License: https://bedlam2.is.tuebingen.mpg.de/license.html
#
# Import shoe textures (color, normal, displacement)
#
# Notes:
# + Unreal 5.3.2 with default Interchange Framework (enabled by default)
#

from pathlib import Path
import unreal

DATA_ROOT = r"C:\bedlam2\textures\shoes\texture_maps"
DATA_ROOT_UNREAL = "/Engine/PS/Bedlam/Shoes/Textures"
def import_textures(texture_paths):

    for texture_path in texture_paths:
        unreal.log(f"Processing {texture_path}")

        # Check if texture is already imported
        # shoe_gso_000\color_map.png
        shoe_name = texture_path.parent.name

        import_tasks = []

        # Color texture
        texture_asset_name = f"T_{shoe_name}_color"
        texture_asset_dir = f"{DATA_ROOT_UNREAL}/{shoe_name}"
        texture_asset_path = f"{texture_asset_dir}/{texture_asset_name}"

        if unreal.EditorAssetLibrary.does_asset_exist(texture_asset_path):
            unreal.log("  Skipping. Already imported: " + texture_asset_path)
        else:
            unreal.log(f"  Importing: '{texture_path}'")
            task = unreal.AssetImportTask()
            task.set_editor_property("filename", str(texture_path))

            # Unreal 5.3.2 uses Interchange Framework which ignores destination_name
            #task.set_editor_property("destination_name", texture_asset_name)

            task.set_editor_property("destination_path", texture_asset_dir)
            task.set_editor_property('save', True)
            import_tasks.append(task)

        # Normal texture
        normal_texture_path = texture_path.parent / texture_path.name.replace("color_map", "normal_map")
        normal_texture_asset_name = f"T_{shoe_name}_normal"
        normal_texture_asset_path = f"{texture_asset_dir}/{normal_texture_asset_name}"

        if unreal.EditorAssetLibrary.does_asset_exist(normal_texture_asset_path):
            unreal.log("  Skipping. Already imported: " + normal_texture_asset_path)
        else:
            unreal.log(f"  Importing normal map: '{normal_texture_path}'")
            task = unreal.AssetImportTask()
            task.set_editor_property("filename", str(normal_texture_path))

            # Unreal 5.3.2 uses Interchange Framework which ignores destination_name
            #task.set_editor_property("destination_name", normal_texture_asset_name)

            task.set_editor_property("destination_path", texture_asset_dir)
            task.set_editor_property('save', True)
            import_tasks.append(task)

        # Displacement map
        displacement_texture_path = texture_path.parent / texture_path.name.replace("color_map", "displacement_map")
        displacement_texture_asset_name = f"T_{shoe_name}_displacement"
        displacement_texture_asset_path = f"{texture_asset_dir}/{displacement_texture_asset_name}"

        if unreal.EditorAssetLibrary.does_asset_exist(displacement_texture_asset_path):
            unreal.log("  Skipping. Already imported: " + displacement_texture_asset_path)
        else:
            unreal.log(f"  Importing displacement map: '{displacement_texture_path}'")
            task = unreal.AssetImportTask()
            task.set_editor_property("filename", str(displacement_texture_path))

            # Unreal 5.3.2 uses Interchange Framework which ignores destination_name
            #task.set_editor_property("destination_name", displacement_texture_asset_name)

            task.set_editor_property("destination_path", texture_asset_dir)
            task.set_editor_property('save', True)
            import_tasks.append(task)

        # Import color, normal and displacement textures
        unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks(import_tasks)

        # Fix displacement map compression
        displacement_texture_asset_path = f"{texture_asset_dir}/displacement_map"
        if unreal.EditorAssetLibrary.does_asset_exist(displacement_texture_asset_path):
            unreal.log(f"  Setting displacement map compression: Grayscale (G8/16): {displacement_texture_asset_path}")

            texture_asset = unreal.EditorAssetLibrary.load_asset(f"Texture2D'{displacement_texture_asset_path}'")
            if not texture_asset:
                unreal.log_error(f"Cannot load displacement texture")
                return False

            # Source data should be LinearGrayscale and import without sRGB so that G8 format will be used.
            # Reason: For sRGB textures B8G8R8A8 will be used instead of R8.
            # Interchange Framework imports LinearGrayscale initially with sRGB=True which needs to be disable.
            texture_asset.set_editor_property("srgb", False)
            texture_asset.set_editor_property("compression_settings", unreal.TextureCompressionSettings.TC_GRAYSCALE)
            unreal.EditorAssetLibrary.save_loaded_asset(texture_asset, only_if_is_dirty=False)

        # Fix names of imported textures to include T_{shoe_name_} prefix
        assets = unreal.EditorAssetLibrary.list_assets(DATA_ROOT_UNREAL, recursive=True, include_folder=False)

        for asset_path in assets:
            # /Engine/PS/Bedlam/Shoes/Textures/shoe_gso_000/color_map.color_map
            asset_directory = asset_path.rsplit("/", maxsplit=1)[0]
            asset_name = asset_path.rsplit("/", maxsplit=1)[1]
            if asset_name.startswith("T_"):
                continue

            shoe_name = asset_directory.rsplit("/", maxsplit=1)[1]
            suffix = ""
            if "color_map" in asset_path:
                suffix = "_color"
            elif "normal_map" in asset_path:
                suffix = "_normal"
            elif "displacement_map" in asset_path:
                suffix = "_displacement"

            # /Engine/PS/Bedlam/Shoes/Textures/shoe_gso_000/T_shoe_gso_000_color
            renamed_asset_path = f"{asset_directory}/T_{shoe_name}{suffix}"

            # /Engine/PS/Bedlam/Shoes/Textures/shoe_gso_000/color_map
            asset_path = asset_path.rsplit(".", maxsplit=1)[0]

            unreal.log(f"  Renaming {asset_path} to {renamed_asset_path}")
            success = unreal.EditorAssetLibrary.rename_asset(asset_path, renamed_asset_path)
            if not success:
                unreal.log_error("Cannot rename texture. Aborting.")
                return False

    return True

######################################################################
# Main
######################################################################
if __name__ == "__main__":
    unreal.log("============================================================")
    unreal.log("Running: %s" % __file__)

    # Build import list
    import_texture_paths = sorted(Path(DATA_ROOT).rglob("color_map.png"))

    success = import_textures(import_texture_paths)
    if success:
        unreal.log("Conversion finished. [SUCCESS]")
    else:
        unreal.log_error("Conversion failed.")
