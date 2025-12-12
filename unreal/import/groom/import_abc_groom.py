# Copyright (c) 2025 Max Planck Society
# License: https://bedlam2.is.tuebingen.mpg.de/license.html
#
# Batch import Alembic .abc groom files into Unreal Engine
# Existing Unreal Grooms assets will be skipped. Manually delete them to force reimport.
#
# Requirements:
# + Enabled Plugins
#   + Alembic Groom Importer
#   + Groom
#

from pathlib import Path
import time
import unreal

data_root = r"C:\bedlam2\groom"
data_root_unreal = "/Engine/PS/Bedlam/Hair/VineFX"

def import_abc(data_root, data_root_unreal):

    # Build import list
    import_abc_paths = sorted(Path(data_root).rglob("*.abc"))

    import_tasks = []
    for import_abc_path in import_abc_paths:

        unreal.log(f"Processing Alembic Groom: {import_abc_path}")
        # unreal.log_flush() # Note: does not update editor console log

        # Check if file is already imported
        uasset_folder = f"{data_root_unreal}"
        uasset_name = import_abc_path.stem
        uasset_path = f"{uasset_folder}/{uasset_name}"

        if unreal.EditorAssetLibrary.does_asset_exist(uasset_path):
            unreal.log("  Skipping import. Already imported: " + uasset_path)
        else:
            unreal.log("  Importing: " + uasset_path)

            # Fix rotation for Grooms which face upwards after import with default rotation (0, 0, 0)
            options = unreal.GroomImportOptions()
            options.conversion_settings = unreal.GroomConversionSettings(rotation=[-90.0, 0.0, 180.0], scale=[1.0, 1.0, 1.0])

            task = unreal.AssetImportTask()
            task.set_editor_property("automated", True)
            task.set_editor_property("filename", str(import_abc_path))
            task.set_editor_property("destination_path", uasset_folder)
            task.set_editor_property("destination_name", "")
            task.set_editor_property("replace_existing", True)
            task.set_editor_property("save", True)
            task.set_editor_property("options", options)

            # Import one ABC at a time and save all imported assets immediately to avoid data loss on Unreal Editor crash
            import_tasks = [task]
            unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks(import_tasks)
            unreal.EditorAssetLibrary.save_directory(data_root_unreal) # save imported materials and textures

######################################################################
# Main
######################################################################
if __name__ == "__main__":
    unreal.log("============================================================")
    unreal.log("Running: %s" % __file__)

    # Import all Alembic files
    start_time = time.perf_counter()
    import_abc(data_root, data_root_unreal)
    print(f"Alembic batch import finished. Total import time: {(time.perf_counter() - start_time):.1f}s")
