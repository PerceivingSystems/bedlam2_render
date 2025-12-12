# Copyright (c) 2025 Max Planck Society
# License: https://bedlam2.is.tuebingen.mpg.de/license.html
#
# Create bindings for imported groom files
#
# Requirements:
# + Enabled Plugins
#   + Alembic Groom Importer
#   + Groom
#

import sys
import unreal

source_geometry_cache_path = "/Engine/PS/Bedlam/Core/SMPLX/smplx_lh_n_abc"

data_root_unreal_groom = "/Engine/PS/Bedlam/Hair/VineFX"
data_root_unreal_geometrycache = "/Engine/PS/Bedlam/SMPLX_LH"

def create_groom_binding_geometrycache(groom_assetdata, source_geometry_cache_asset, target_geometry_cache_assets, data_root_unreal_bindings):
    unreal.log(f"Generating groom bindings (geometry cache) for hair asset: {groom_assetdata.package_name}")
    groom_asset = groom_assetdata.get_asset()
    for target_geometry_cache_assetdata in target_geometry_cache_assets:
        subject_name = str(target_geometry_cache_assetdata.asset_name).rsplit("_", maxsplit=1)[0]
        desired_package_name = f"{data_root_unreal_bindings}/{subject_name}/{groom_assetdata.asset_name}_{subject_name}"
        if unreal.EditorAssetLibrary.does_asset_exist(desired_package_name):
            unreal.log_warning(f"  Skipping. Binding already exists: {desired_package_name}")
            continue

        unreal.log(f"  Creating: {desired_package_name}")

        binding = unreal.GroomLibrary.create_new_geometry_cache_groom_binding_asset_with_path(f"{desired_package_name}",
                                                                                              groom_asset,
                                                                                              target_geometry_cache_assetdata.get_asset(),
                                                                                              100,
                                                                                              source_geometry_cache_asset)

        if binding is None:
            unreal.log_error("[ERROR] Binding creation failed")
            return False

    return True

######################################################################
# Main
######################################################################
if __name__ == "__main__":
    unreal.log("============================================================")
    unreal.log("Running: %s" % __file__)

    # Load source geometry cache reference which corresponds to groom authoring reference mesh (SMPL-X, locked_head, neutral)
    source_geometry_cache_asset = unreal.EditorAssetLibrary.load_asset(f"GeometryCache'{source_geometry_cache_path}'")
    if source_geometry_cache_asset is None:
        unreal.log_error(f"Cannot load source geometry cache: {source_geometry_cache_path}")
        sys.exit(1)

    asset_registry = unreal.AssetRegistryHelpers.get_asset_registry()

    # Get grooms
    # Note: Using class_names is deprecated
    filter = unreal.ARFilter(package_paths=[data_root_unreal_groom], recursive_paths=True, class_names=[unreal.GroomAsset.static_class().get_name()])
    groom_assets = asset_registry.get_assets(filter)
    groom_assets = sorted(groom_assets, key=lambda x: x.asset_name)

    # Get target geometry cache assets
    target_geometry_cache_assets = []
    filter = unreal.ARFilter(package_paths=[data_root_unreal_geometrycache], recursive_paths=True, class_names=[unreal.GeometryCache.static_class().get_name()])
    geometry_cache_assets = asset_registry.get_assets(filter)
    for geometry_cache_asset in geometry_cache_assets:
        if str(geometry_cache_asset.asset_name).endswith("_0000"): # files with _0000 suffix denote shape only GeometryCache in default T-pose
            target_geometry_cache_assets.append(geometry_cache_asset)

    target_geometry_cache_assets = sorted(target_geometry_cache_assets, key=lambda x: x.asset_name)

    data_root_unreal_bindings = f"{data_root_unreal_groom}/Bindings/GeometryCache"
    unreal.EditorAssetLibrary.make_directory(data_root_unreal_bindings)
    for groom_assetdata in groom_assets:
        create_groom_binding_geometrycache(groom_assetdata, source_geometry_cache_asset, target_geometry_cache_assets, data_root_unreal_bindings)
