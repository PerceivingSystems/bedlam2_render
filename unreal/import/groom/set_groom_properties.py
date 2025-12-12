# Copyright (c) 2025 Max Planck Society
# License: https://bedlam2.is.tuebingen.mpg.de/license.html
#
# Set Groom properties from CSV file for selected Content Browser Groom assets
#
# Requirements: Enabled Groom Plugin
#

import csv
import unreal

csv_path = r"C:\bedlam2\render\unreal\import\groom\groom_properties.csv"

######################################################################
# Main
######################################################################
if __name__ == "__main__":
    unreal.log("============================================================")
    unreal.log("Running: %s" % __file__)

    csv_reader = None
    groom_properties = {}
    with open(csv_path, mode="r") as csv_file:
        csv_reader = csv.DictReader(csv_file)
        csv_rows = list(csv_reader)

        for row in csv_rows:
            groom_name = row["groom_name"]
            hair_width = float(row["hair_width"])
            groom_properties[groom_name] = hair_width

    selection = unreal.EditorUtilityLibrary.get_selected_assets() # Loads all selected assets into memory
    for asset in selection:
        if not isinstance(asset, unreal.GroomAsset):
            unreal.log_warning(f"  Ignoring (no GroomAsset): {asset.get_full_name()}")
            continue

        groom_name = asset.get_name()
        hair_width = groom_properties[groom_name]

        unreal.log(f"Setting properties for groom: {groom_name}")

        # Rendering
        unreal.log(f"  hair width: {hair_width}")
        hair_groups_rendering = asset.get_editor_property("hair_groups_rendering")
        num_hair_groups = len(hair_groups_rendering)
        for index in range(num_hair_groups):
            rendering = hair_groups_rendering[index]
            geometry_settings = rendering.get_editor_property("geometry_settings")
            geometry_settings.set_editor_property("hair_width", hair_width)
            hair_groups_rendering[index] = rendering

        # Save changes to disk
        # Note: asset.get_path_name() results in ObjectPath which is deprecated parameter for save_asset()
        unreal.EditorAssetLibrary.save_asset(asset.get_outer().get_name(), only_if_is_dirty=False)
