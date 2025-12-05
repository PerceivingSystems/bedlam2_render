# Copyright (c) 2025 Max Planck Society
# License: https://bedlam2.is.tuebingen.mpg.de/license.html
#
# Batch import SMPL-X .fbx files into Unreal Engine
#

import math
from pathlib import Path
import sys
import time
import unreal

data_root = r"C:\bedlam2\animations\fbx"

whitelist_subjects_path = None

whitelist_animations_path = None

data_root_unreal = "/Engine/PS/Bedlam/SMPLX_LH_animations"

def import_fbx(data_root, data_root_unreal, current_batch, num_batches, whitelist_subjects=None, whitelist_animations=None):

    # Build import list
    import_fbx_paths = sorted(Path(data_root).rglob("*.fbx"))

    if current_batch is not None:
        section_length = math.ceil(len(import_fbx_paths)/num_batches)
        start_index = current_batch * section_length
        end_index = start_index + section_length
        if end_index > len(import_fbx_paths):
            end_index = len(import_fbx_paths)
        print(f"Processing section: {current_batch}, total sections: {num_batches}, range: [{start_index}:{end_index}]")
        import_fbx_paths = import_fbx_paths[start_index : end_index]

    import_tasks = []
    for import_fbx_path in import_fbx_paths:

        if whitelist_subjects is not None:
            current_subject_name = import_fbx_path.parent.name
            if current_subject_name not in whitelist_subjects:
                unreal.log(f"Skipping FBX. Subject not whitelisted: {import_fbx_path}")
                continue

        if whitelist_animations is not None:
            current_animation_name = import_fbx_path.stem.split("_")[-1]
            if current_animation_name not in whitelist_animations:
                unreal.log(f"Skipping FBX. Animation not whitelisted: {import_fbx_path}")
                continue

        unreal.log(f"Processing FBX: {import_fbx_path}")

        # Check if file is already imported
        uasset_folder_name = import_fbx_path.parent.name
        uasset_folder = f"{data_root_unreal}/{uasset_folder_name}"
        uasset_name = import_fbx_path.stem
        uasset_path = f"{uasset_folder}/{uasset_name}"

        if unreal.EditorAssetLibrary.does_asset_exist(uasset_path):
            unreal.log("  Skipping import. Already imported: " + uasset_path)
        else:
            unreal.log("  Importing: " + uasset_path)

            fbx_options = unreal.FbxImportUI()
            fbx_options.set_editor_property('import_as_skeletal', True)
            fbx_options.set_editor_property('import_animations', True)
            fbx_options.set_editor_property('import_materials', False)
            fbx_options.set_editor_property('import_textures', False)

            task = unreal.AssetImportTask()
            task.set_editor_property("automated", True)
            task.set_editor_property("filename", str(import_fbx_path))
            task.set_editor_property("destination_path", uasset_folder)
            task.set_editor_property("destination_name", "")
            task.set_editor_property("replace_existing", True)
            task.set_editor_property("save", True)
            task.set_editor_property("options", fbx_options)

            # Import one FBX at a time and save all imported assets immediately to avoid data loss on Unreal Editor crash
            import_tasks = [task]
            unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks(import_tasks)
            unreal.EditorAssetLibrary.save_directory(data_root_unreal) # save imported materials and textures

######################################################################
# Main
######################################################################
if __name__ == "__main__":
    unreal.log("============================================================")
    unreal.log("Running: %s" % __file__)

    current_batch = None
    num_batches = None
    if len(sys.argv) == 3:
        current_batch = int(sys.argv[1])
        num_batches = int(sys.argv[2])

    whitelist_subjects = None
    if whitelist_subjects_path is not None:
        with open(whitelist_subjects_path) as f:
            whitelist_subjects = f.read().splitlines()

    whitelist_animations = None
    if whitelist_animations_path is not None:
        with open(whitelist_animations_path) as f:
            whitelist_animations = f.read().splitlines()

    start_time = time.perf_counter()
    import_fbx(data_root, data_root_unreal, current_batch, num_batches, whitelist_subjects, whitelist_animations)
    print(f"FBX batch import finished. Total import time: {(time.perf_counter() - start_time):.1f}s")
