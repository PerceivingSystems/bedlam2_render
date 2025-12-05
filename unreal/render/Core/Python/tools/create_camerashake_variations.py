# Copyright (c) 2025 Max Planck Society
# License: https://bedlam2.is.tuebingen.mpg.de/license.html
#
# Create copies of template camera shake with randomized seed values for Perlin noise.
#
# Requirements: BEDLAM engine plugin
#
from pathlib import Path
import random
import sys
import unreal

NUM_VARIATIONS=250
MAX_SEED=254 # use same maximum seed value as default Unreal Perlin shake randomization (0-254)
#SHAKE_TEMPLATE_PATH="/BEDLAM/CameraShake/BE_CameraShake_LowFrequency"
SHAKE_TEMPLATE_PATH="/BEDLAM/CameraShake/BE_CameraShake_HighFrequency"
TARGET_ROOT="/Engine/PS/Bedlam/Core/Camera/ShakeVariations"

def create_seeds(max_seed):
    seeds = {}
    seeds["x"]     = list(range(max_seed))
    seeds["y"]     = list(range(max_seed))
    seeds["z"]     = list(range(max_seed))
    seeds["pitch"] = list(range(max_seed))
    seeds["roll"]  = list(range(max_seed))
    seeds["yaw"]   = list(range(max_seed))
    seeds["fov"]   = list(range(max_seed))
    for name in seeds:
        random.shuffle(seeds[name])

    return seeds

def create_shake_variations(shake_template_path, num_variations, max_seed):
    shake_name = shake_template_path.rsplit("/", maxsplit=1)[1]

    seeds = create_seeds(max_seed)

    for index in range(num_variations):
        target_shake_path = f"{TARGET_ROOT}/{shake_name}/{shake_name}_{index:03d}"

        unreal.log(f"Duplicating asset: {shake_template_path} => {target_shake_path}")
        target_shake_asset = unreal.EditorAssetLibrary.duplicate_asset(shake_template_path, target_shake_path)
        if target_shake_asset is None:
            unreal.log_error("ERROR: Cannot duplicate asset")
            return False

        target_shake_name =  target_shake_path.rsplit("/", maxsplit=1)[1]
        shake_class_path = f"{target_shake_path}.{target_shake_name}_C"
        shake_class = unreal.load_object(None, shake_class_path)
        do = unreal.get_default_object(shake_class)
        shake_pattern = do.get_root_shake_pattern()

        # Reshuffle if we create more templates than seeds
        if len(seeds["x"]) == 0:
            seeds = create_seeds()

        shake_pattern.initial_location_offset_seed_x = seeds["x"].pop()
        shake_pattern.initial_location_offset_seed_y = seeds["y"].pop()
        shake_pattern.initial_location_offset_seed_z = seeds["z"].pop()
        shake_pattern.initial_rotation_offset_seed_pitch = seeds["pitch"].pop()
        shake_pattern.initial_rotation_offset_seed_roll = seeds["roll"].pop()
        shake_pattern.initial_rotation_offset_seed_yaw = seeds["yaw"].pop()
        shake_pattern.initial_fov_offset_seed = seeds["fov"].pop()

        unreal.EditorAssetLibrary.save_loaded_asset(target_shake_asset)


    return True

if __name__ == '__main__':
    unreal.log("============================================================")
    unreal.log("Running: %s" % __file__)

    success = create_shake_variations(SHAKE_TEMPLATE_PATH, NUM_VARIATIONS, MAX_SEED)

    if success:
        unreal.log(f"CameraShake variations generated")
        sys.exit(0)
    else:
        unreal.log_error(f"ERROR: CameraShake variation generation failed")
        sys.exit(1)
