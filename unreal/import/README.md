# Unreal Import Scripts
The various scripts in this folder help with automating BEDLAM2 related data import into Unreal.

They can be used to import new data which is not included in the BEDLAM2 Unreal Assets Starter Pack.

See source file headers for additional information.

Requirements:
  + Unreal Engine 5.3.2 with active [Python Editor Script Plugin](https://dev.epicgames.com/documentation/en-us/unreal-engine/scripting-the-unreal-editor-using-python?application_version=5.3)

Related items:
+ BEDLAM2 Unreal Assets Starter Pack (BE_UASP)
  + Includes Unreal 5.3.2 assets which were imported using these helper scripts
    + Format: `.uasset` (Unreal 5.3.2)
  + Available in download area of [BEDLAM2 website](https://bedlam2.is.tuebingen.mpg.de/)
  + Subset of bodies/clothing used for rendering of BEDLAM2 dataset
  + Starter pack asset groups
    + Animated bodies: BE_UASP_SMPLXLH
    + Body textures: BE_UASP_SMPLXTextures
    + Simulated clothing and textures (BE_UASP_Clothing)
    + HDR images: BE_UASP_HDRI
    + Hair: BE_UASP_Hair
      + Strand-based grooms
    + Shoes: BE_UASP_Shoes
      + Displacement maps and color textures for toeless SMPL-X modification

## Animated SMPL-X bodies
+ [import_abc_smplx_batch.py](import_abc_smplx_batch.py)
+ Use this script to batch import SMPL-X Alembic ABC files as `GeometryCache`
+ Requirements
    + Python for Windows (3.10.6 or later)
    + Blank `BE_Import` Unreal project (no default map) with the following active plugins
      + Plugins
        + Python Editor Script Plugin
        + Alembic Importer

+ Usage
    + Adjust data paths at top of `import_abc_smplx_batch.py` and `import_abc_smplx.py` scripts
    + Close all open Unreal Editor instances
    + Run multiprocess batch import from Windows command prompt. The example below imports 100 data batches using 10 simultaneous Unreal Engine instances. Depending on your available CPU core count, available main memory (128GB+ recommended) and amount of source files, you can increase or need to decrease the amount of processes. For fastest processing of BEDLAM2 motion release data make sure that you have a fast SSD with large enough space (1TB).
        + `py -3 import_abc_smplx_batch.py 100 10`

## Animated SMPL-X bodies with joints
+ [import_fbx_smplx_batch.py](import_fbx_smplx_batch.py)
+ Use this script to batch import SMPL-X FBX files as `SkeletalMesh`
+ This is needed if you want to target specific body parts with the camera
+ Requirements
    + Python for Windows (3.10.6 or later)
    + Blank `BE_Import` Unreal project (no default map) with the following active plugins
      + Plugins
        + Python Editor Script Plugin
        + Interchange Framework
+ Usage
    + Adjust data paths at top of `import_fbx_smplx_batch.py` and `import_fbx_smplx.py` scripts
    + Close all open Unreal Editor instances
    + Run multiprocess batch import from Windows command prompt. The example below imports 100 data batches using 5 simultaneous Unreal Engine instances. Depending on your available CPU core count, available CPU main memory (128GB+ recommended), available GPU memory and amount of source files, you can increase or need to decrease the amount of processes. For fastest processing of BEDLAM2 motion release data make sure that you have a fast SSD with large enough space (1TB).
        + `py -3 import_fbx_smplx_batch.py 100 5`

## Simulated animated clothing
+ [import_abc_clothing_batch.py](import_abc_clothing_batch.py)
+ Use this script to batch import simulated 3D clothing files in Alembic ABC format as `Geometry Cache`
+ Requirements
    + Python for Windows (3.10.6 or later)
    + Blank `BE_Import` Unreal project (no default map) with the following active plugins
      + Plugins
        + Python Editor Script Plugin
        + Alembic Importer
+ Usage
    + Download and extract source data
      + Source data: BEDLAM2 simulated clothing cache in Alembic `.abc` format
        + BEDLAM2 website>Downloads>Clothing>ABC format
          + `b2_clothing_abc*.tar`
    + Adjust data paths at top of `import_abc_clothing_batch.py` and `import_abc_clothing.py` scripts
    + Close all open Unreal Editor instances
    + Run multiprocess batch import from Windows command prompt. The example below imports 300 data batches using 10 simultaneous Unreal Engine instances. Depending on your available CPU core count and available main memory (128GB+ recommended) you can increase or need to decrease the amount of processes. For fastest processing of BEDLAM2 clothing release data make sure that you have a fast SSD with large enough space (3TB).
        + `py -3 import_abc_clothing_batch.py 300 10`

## Body textures
+ The following import scripts are not needed if you use the BE_UASP_SMPLXTextures starter pack which contains all released 100 SMPL-X body textures in `.uasset` format
+ [create_body_materials.py](create_body_materials.py)
+ Use this script to generate required `MaterialInstance` materials for imported BEDLAM2 body textures
+ Requirements
    + BEDLAM2 BE_Core Unreal assets installed under your UE5.3 install directory. See [Unreal render README](../render/README.md) for instructions.
    + Imported BEDLAM2 body textures
        + Download body textures from BEDLAM2 website and extract to local folder
          + BEDLAM2 website>Downloads>Body Textures With Bald Head
            + `bedlam2_body_textures_meshcapade.zip`
        + Load Unreal Editor project
        + Make sure that "Show Engine Content" is activated in Content Browser settings so that you see the `Engine` folder hierarchy
        + Create `Engine/Content/PS/Meshcapade/SMPLX` folder via Content Browser
        + Import local `bedlam2_body_textures_meshcapade/bald/` body texture folder contents via Content Browser to `Engine/Content/PS/Meshcapade/SMPLX/Textures/bald/`
        + Content Browser>Save All

+ Usage
    + Select all imported body textures under `Engine/Content/PS/Meshcapade/SMPLX/bald/` in Content Browser (Filter:Texture, CTRL-A)
    + Run script via Execute Python Script
    + Content Browser>Save All

## Clothing textures
+ [import_clothing_textures.py](import_clothing_textures.py)
+ Use this script to import downloaded BEDLAM2 3D clothing textures and generate required `MaterialInstance` materials for them
+ Requirements:
    + BEDLAM2 BE_Core Unreal assets installed under your UE5.3 install directory. See [Unreal render README](../render/README.md) for instructions.
    + BEDLAM2 clothing textures
    + Download clothing textures from BEDLAM2 website and extract to local folder
      + BEDLAM2 website>Downloads>Clothing>Clothing textures
        + `b2_clothing_textures_*.tar`

+ Usage
    + Follow instructions at top of script
    + Adjust data paths at top of script
    + Run script via Execute Python Script
    + Content Browser>Save All

## HDR images
+ [import_hdr.py](import_hdr.py)
  + Not needed if you only use the HDR images in the BE_UASP_HDRI starter pack
+ Use this script to import panoramic high-dynamic range images in HDR format for image-based lighting
    + Not needed for existing 3D environments from Unreal Marketplace
+ [List of used BEDLAM2 HDR images](../../config/whitelist_hdri.txt)
    + HDR Source: https://polyhaven.com/hdris
      + [Support Poly Haven via Patreon](https://www.patreon.com/cw/polyhaven)
    + 8K HDR version (8192x4096)
+ Usage
    + Download desired 8K HDRI images in HDR format
    + Adjust data paths at top of script
    + Run script via Execute Python Script
    + Disable Mipmaps and use Skybox Texture Group for all imported HDR images
        + Select all imported HDR images
        + Asset Actions>Edit Selection in Property Matrix
            + Select all rows
            + LevelOfDetail
                + Mip Gen Settings: NoMipmaps
                + Texture Group: Skybox
            + Save

## Hair
+ [import_abc_groom.py](groom/import_abc_groom.py)
  + Batch import Alembic .abc groom files into Unreal Engine
  + Not needed if you use the BE_UASP_Hair starter pack
  + See file header for plugin requirements
  + Source data: BEDLAM2 hair grooms in Alembic `abc` format
    + BEDLAM2 website>Downloads>Hair>Grooms in abc format
        + `b2_groom_abc.tar.gz`
  + Adjust data paths at top of script
  + Run script via Execute Python Script

+ [set_groom_properties.py](groom/set_groom_properties.py)
  + Not needed if you use the BE_UASP_Hair starter pack
  + Apply individual Strands Hair Width settings for selected Content Browser Groom assets
+ [create_groom_bindings.py](groom/create_groom_bindings.py)
  + Create GeometryCache groom binding assets for all available target body shapes
    + Needed to adapt the default hair grooms to indidual head shapes of target bodies
  + Requires shape-only GeometryCache in default T-pose (`_0000.uasset` suffix) for each target body shape
    + Run `tools/animations/convert_to_tpose_npz.py` to convert new BEDLAM2 SMPL-X motions to static T-pose
      + `_0000.npz` suffix
    + Convert new T-pose .npz files to .abc files
      + `blender/smplx_anim_to_alembic/`
    + Import these new T-pose .abc files into Unreal
      + See `Animated SMPL-X bodies` section above

## Shoes
The following import scripts are not needed if you use the BE_UASP_Shoes starter pack and only use the released BEDLAM2 body textures
+ [import_shoe_textures.py](shoes/import_shoe_textures.py)
  + Import shoe textures (color, normal, displacement)
  + Usage
    + Download and extract source data
      + Source data: BEDLAM2 shoe texture maps
        + BEDLAM2 website>Downloads>Shoes>Texture maps
          + `b2_shoes.tar.gz`
      + Adjust data paths at top of script
      + Run script via Execute Python Script

+ [create_body_shoe_materials.py](shoes/create_body_shoe_materials.py)
  + Generate MaterialInstances for all available body texture and shoe type combinations
